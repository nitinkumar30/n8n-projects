# TracedIP Bot — Implementation Guide

Technical deep-dive into the n8n workflow architecture, node configurations, and integration logic.

---

## Workflow Overview

The workflow is exported as a single **n8n JSON file** (`ipstack-telegram-bot_workflow.json`) containing **17 interconnected nodes**. It follows a branching pipeline pattern: parse → validate → route → fetch → transform → enrich → format → deliver.

---

## Node-by-Node Breakdown

### 1. Telegram Trigger

- **Type:** `n8n-nodes-base.telegramTrigger`
- **Purpose:** Listens for incoming Telegram messages via webhook
- **Configuration:** Trigger on `message` events with all allowed updates enabled
- **Credential:** n8n Telegram credential (bot token from BotFather)

### 2. Parse Command

- **Type:** `n8n-nodes-base.code` (JavaScript)
- **Mode:** Run Once for All Items
- **Purpose:** Extracts and validates the command from the message text

**Logic:**
- Splits message text by whitespace to extract command and arguments
- For `/ip`: validates single IPv4 (octet range 0–255) or IPv6 (simplified colon-hex pattern)
- For `/bulk`: validates each IP, enforces 50 IP maximum, separates valid/invalid
- For `/myip`: no validation needed
- Returns `{ command, chatId, ip/ips, valid, error? }`

**Validation regex:**
```
IPv4: /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/
IPv6: /^([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4}$/
```

### 3. Route Command

- **Type:** `n8n-nodes-base.switch`
- **Purpose:** Routes to the correct execution branch based on command
- **Routing rules:**
  - Output 0: `/ip`
  - Output 1: `/myip`
  - Output 2: `/bulk`
  - Output 3: default (unknown command → error)

### 4. IP Valid Check / Bulk Valid Check

- **Type:** `n8n-nodes-base.if`
- **Purpose:** Validated items proceed to API calls; invalid items are sent to the error handler
- **Condition:** `$json.valid === true`

### 5. IPStack API Nodes (3x)

- **Type:** `n8n-nodes-base.httpRequest` (v4.2)
- **Continue on Fail:** `true` (graceful error handling)

| Node | Endpoint | URL |
|------|----------|-----|
| IPStack Single Lookup | `GET /{ip}` | `https://api.ipstack.com/{{ $json.ip }}?access_key={{ $env.IPSTACK_ACCESS_KEY }}` |
| IPStack MyIP Lookup | `GET /check` | `https://api.ipstack.com/check?access_key={{ $env.IPSTACK_ACCESS_KEY }}` |
| IPStack Bulk Lookup | `GET /{csv}` | `https://api.ipstack.com/{{ $json.ipsCsv }}?access_key={{ $env.IPSTACK_ACCESS_KEY }}` |

**Timeouts:** 15s (single/check), 30s (bulk)

### 6. Transform & Derive Intelligence

- **Type:** `n8n-nodes-base.code` (JavaScript)
- **Purpose:** The core intelligence engine — transforms raw IPStack JSON into structured intelligence data

**This node performs 5 major operations:**

#### A. Error Checking
Detects and propagates HTTP errors (`httpStatus >= 400`), API errors (`success === false`), and passes through valid responses. If an error is detected, returns immediately with the error message.

#### B. Verified Information Extraction
Maps the raw IPStack response into a structured `verified` object with 7 sub-categories:
- **Network:** IP, hostname, version, ASN, ISP, organization, org type
- **Location:** Country, region, city, ZIP, coordinates, capital
- **Geography:** Continent, flag emoji, calling code, EU membership
- **Time:** Timezone ID, current time, UTC offset, DST status
- **Economy:** Currency name, code, symbol
- **Languages:** Name, native name, code
- **Security:** Proxy status, TOR status, crawler status, VPN, hosting, anonymizer, threat level/types

All fields default to `'N/A'` when missing from the API response.

#### C. Cloud Provider Detection
Heuristic detection checking ISP and organization names against known cloud providers. Detection order (first match wins):

| Provider | ISP/Org Match Patterns |
|----------|----------------------|
| AWS | `amazon`, `aws` |
| Azure | `microsoft`, `azure` |
| GCP | `google.*cloud`, `gcp`, `google llc` |
| Cloudflare | `cloudflare` |
| DigitalOcean | `digitalocean` |
| Linode | `linode`, `akamai` |
| Hetzner | `hetzner` |
| OVHcloud | `ovh` |
| Oracle Cloud | `oracle` |
| IBM Cloud | `ibm.*cloud`, `softlayer` |
| Vultr | `vultr` |
| Scaleway | `scaleway` |
| UpCloud | `upcloud` |

#### D. Network Category Classification
Classifies the IP's network role using a priority-based system:
1. Hosting/Cloud (if `is_hosting` or cloud provider detected)
2. VPN Service
3. Proxy Service
4. TOR Exit Node
5. Mobile/Cellular (carrier keywords)
6. Residential ISP (broadband keywords)
7. Educational Network (`.edu`, university keywords)
8. Government Network (`.gov`, government keywords)
9. Business/Enterprise (org type)

#### E. Geographic Analysis
- **Hemisphere:** Determines Northern/Southern (latitude) and Eastern/Western (longitude)
- **Map Links:** Generates Google Maps and OpenStreetMap URLs from coordinates

#### F. Time Analysis
Parses the `current_time` from IPStack and calculates:
- Local time (12-hour format)
- Local date (full weekday, month, day, year)
- UTC and GMT representations
- Business hours status (9 AM–5 PM, weekdays only)

#### G. Risk Engine
Scoring system with weighted risk factors:

| Indicator | Weight |
|-----------|--------|
| Proxy Service | +40 |
| TOR Node | +50 |
| Web Crawler | +20 |
| VPN Service | +30 |
| Medium Threat Level | +30 |
| High Threat Level | +70 |
| Anonymizer | +45 |

**Outputs:**
- **Risk Score:** 0–100 (capped)
- **Threat Meter:** 10-segment visual bar (🟩 = risk, ⬜ = safe)
- **Classification:** 🟢 Low (≤30) / 🟡 Medium (≤60) / 🔴 High (>60)
- **Trust Rating:** Trusted (≤15) / Suspicious (≤50) / Dangerous (>50)

### 7. Enrichment Nodes (3 parallel branches)

After the Transform node, the data forks into 3 parallel branches:

| Branch | API | URL | Purpose |
|--------|-----|-----|---------|
| Weather | Open-Meteo | `https://api.open-meteo.com/v1/forecast?latitude=...&longitude=...&current=temperature_2m,relative_humidity_2m,wind_speed_10m` | Current weather at IP location |
| Sunrise/Sunset | sunrise-sunset.org | `https://api.sunrise-sunset.org/json?lat=...&lng=...&formatted=0` | Sunrise/sunset times |
| Pass Through | — | — | Preserves main data for merge |

All enrichment nodes use `continueOnFail: true` and 10s timeouts.

### 8. Merge Enrichment Data

- **Type:** `n8n-nodes-base.merge`
- **Mode:** Combine — Merge by Position
- **Purpose:** Combines the main data branch with weather and sunrise enrichments into a single item

### 9. Format Single Report

- **Type:** `n8n-nodes-base.code` (JavaScript)
- **Mode:** Run Once for All Items
- **Purpose:** Builds the full Telegram message string with all 5 report sections

**Message structure:**
```
🔍 IP INTELLIGENCE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━

📌 VERIFIED INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━

🌐 NETWORK
▫ IP Address: `8.8.8.8`
▫ Hostname: `dns.google`
...

📍 LOCATION
▫ Country: 🇺🇸 United States (US)
...

🧠 DERIVED INTELLIGENCE
━━━━━━━━━━━━━━━━━━━━━━━━

🌐 NETWORK ANALYSIS
▫ Cloud Provider: ☁️ Google Cloud (GCP)
...

⚠️ RISK ASSESSMENT
▫ Risk Score: 10/100
▫ Threat Meter: 🟩⬜⬜⬜⬜⬜⬜⬜⬜⬜
...

🔮 ENRICHED INTELLIGENCE
━━━━━━━━━━━━━━━━━━━━━━━━

🌤 WEATHER
▫ Temperature: 22°C
...

📊 EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━

This IP belongs to Google LLC...

⚠️ REPORT NOTES
━━━━━━━━━━━━━━━━━━━━━━━━
...
```

### 10. Format Bulk Report

- **Type:** `n8n-nodes-base.code` (JavaScript)
- **Mode:** Run Once for All Items
- **Purpose:** Builds a compact comparison table for bulk lookups

**Output format (code block):**
```
IP                      │ Country        │ ISP                       │ Risk
─────────────────────────────────────────────────────────────────────────
8.8.8.8                 │ 🇺🇸 US          │ Google LLC                │ 🟢 Low
1.1.1.1                 │ 🇦🇺 AU          │ Cloudflare Inc.           │ 🟢 Low
9.9.9.9                 │ 🇺🇸 US          │ Quad9                     │ 🟢 Low
```

### 11. Telegram Send

- **Type:** `n8n-nodes-base.telegram`
- **Operation:** `sendMessage`
- **Parse Mode:** Markdown (from `$json.parse_mode`)
- **Chat ID:** `{{ $json.chatId }}`

### 12. Error Send

- **Type:** `n8n-nodes-base.telegram`
- **Operation:** `sendMessage`
- **Parse Mode:** `Markdown`
- **Purpose:** Centralized error handler for validation failures, API errors, and unknown commands

---

## Error Handling Strategy

| Layer | Mechanism |
|-------|-----------|
| Input Validation | Parse Command validates IP format before any API call |
| API Errors | `continueOnFail: true` on all HTTP nodes prevents workflow crashes |
| Error Detection | Transform node checks `httpStatus`, `success`, and `error` fields |
| Error Display | Errors are sent to `Error Send` node (validation errors) or caught in Format nodes (API errors) |
| User Feedback | All errors include emoji indicators and clear explanations |

---

## Deployment

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `IPSTACK_ACCESS_KEY` | Yes | Your IPStack API key |

### n8n Credentials

| Credential | Type | Used By |
|------------|------|---------|
| Telegram Bot | Telegram | Telegram Trigger, Telegram Send, Error Send |

### Importing

1. Open n8n dashboard
2. Go to **Workflows → Add Workflow → Import from File**
3. Select `ipstack-telegram-bot_workflow.json`
4. Add your Telegram credential to both the Trigger and Send nodes
5. Set the `IPSTACK_ACCESS_KEY` environment variable
6. Activate the workflow
7. Send `/myip` to your bot to test

---

## Extending the Bot

### Adding AbuseIPDB Integration
Add a new HTTP Request node after Transform & Derive:
- URL: `https://api.abuseipdb.com/api/v2/check?ipAddress={{ $json.ip }}`
- Headers: `Key: {{ $env.ABUSEIPDB_API_KEY }}`, `Accept: application/json`
- Add to merge and format nodes

### Adding VirusTotal Integration
- URL: `https://www.virustotal.com/api/v3/ip_addresses/{{ $json.ip }}`
- Headers: `x-apikey: {{ $env.VIRUSTOTAL_API_KEY }}`

### Adding ASN Intelligence
- URL: `https://api.bgpview.io/asn/{{ $json.verified.asn }}` (free, no key)

---

## Limitations

- IPStack free tier: 100 requests/month
- Telegram message limit: 4096 characters (reports may need splitting for very long enrichments)
- Geolocation accuracy varies by IP type and region
- Cloud provider detection is heuristic-based (ISP name matching) and may produce false negatives
