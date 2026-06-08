# n8n Telegram Bot Projects

[![n8n](https://img.shields.io/badge/engine-n8n-%23EA4AAA?style=flat-square&logo=n8n)](https://n8n.io)
[![Telegram](https://img.shields.io/badge/chat-Telegram-%2326A5E4?style=flat-square&logo=telegram)](https://core.telegram.org/bots/api)
[![Cloudflare](https://img.shields.io/badge/tunnel-Cloudflare-F38020?style=flat-square&logo=cloudflare)](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success?style=flat-square)](#)

A collection of production-ready **Telegram bots** built on **n8n** — the open-source workflow automation platform. Each bot runs locally on your machine, exposed to the internet via **Cloudflare Tunnel** for free HTTPS, and is managed by Python launcher scripts for zero-touch startup.

---

## Project Catalog

| Project | Description | Nodes | Key API | Status |
|---------|-------------|-------|---------|--------|
| [QR Code Generator Bot](#qr-code-generator-bot) | Generate QR codes from any URL via Telegram | 4 | QRServer API | Active |
| [TracedIP Intelligence Bot](#tracedip-ip-intelligence-bot) | Full OSINT IP lookup with risk scoring | 10 | IPStack API | Active |

---

## QR Code Generator Bot

**Folder:** `QR_code_generator/` · **Workflow:** `Telegram bot - QR code generator.json`

A Telegram bot that accepts URLs from users, validates them, generates a QR code via the QRServer API, and sends the image back — all running continuously through a free Cloudflare Tunnel.

### What It Does

```
User sends "https://github.com"
  → Bot validates the URL
  → Calls QRServer API with styled parameters
  → Sends QR code image back to user
```

### Architecture

```
Telegram User
    ↓
Telegram Servers
    ↓
Cloudflare HTTPS Tunnel (free, stable)
    ↓
Local n8n instance (webhook listener)
    ↓
QR Generation Workflow
    ↓
Telegram Send Photo (QR image)
```

### Tech Stack

| Tool | Purpose |
|------|---------|
| **n8n** | Workflow automation engine |
| **Telegram Bot API** | Receive messages + send QR images |
| **Cloudflare Tunnel (cloudflared)** | Free HTTPS public tunnel |
| **QRServer API** | QR code generation |
| **Python** | Auto-start script (tunnel + env vars + n8n) |

### Workflow Nodes (4)

| # | Node | Type | Function |
|---|------|------|----------|
| 1 | Telegram Trigger | `telegramTrigger` | Listens for incoming messages |
| 2 | IF Node | `if` | Validates URL via regex `^(https?:\/\/)[^\s]+$` |
| 3 | HTTP Request | `httpRequest` | Calls `api.qrserver.com/v1/create-qr-code/` with styled params |
| 4 | Telegram Send Photo | `telegram` | Replies with the QR image + caption |

### Setup

1. Install **n8n**: `npm install -g n8n`
2. Install **Python 3** (add to PATH)
3. Install **Cloudflare Tunnel**: [download cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)
4. Create a Telegram bot via [@BotFather](https://t.me/botfather) — save the token
5. Import the workflow JSON into n8n (port 5678)
6. Configure Telegram Trigger with your bot token
7. Click **ACTIVE** (top-right) — never use "Test Workflow" for production

### Run

```bash
python QR_code_generator/RUN_CONFIG_AUTO.py
```

Or from root:

```bash
python start_n8n.py
```

The script automatically:
- Starts Cloudflare Tunnel
- Extracts the public HTTPS URL
- Sets `WEBHOOK_URL`, `N8N_PROTOCOL`, `N8N_HOST`
- Starts n8n
- Keeps everything running

### Usage

```
Send: https://github.com
  → Bot replies with QR code image

Send: hello
  → Bot replies: "❌ Please send valid URL"
```

### Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| HTTPS webhook error | localhost / HTTP used | Use Cloudflare Tunnel |
| Trigger works only once | Using "Test Workflow" | Click **ACTIVE** instead |
| Webhook conflict | Testing + Active simultaneously | Only use ACTIVE mode |

### Files

| File | Purpose |
|------|---------|
| `Telegram bot - QR code generator.json` | Exported n8n workflow (import this) |
| `RUN_CONFIG_AUTO.py` | Auto-start script (Cloudflare + env + n8n) |
| `start_n8n.py` | Single-project launcher |
| `start_all_projects.py` | Multi-project launcher |
| `images/` | Screenshots and diagrams |
| `CONFIG.MD` | Legacy ngrok setup guide (reference only) |

---

## TracedIP — IP Intelligence Bot

**Folder:** `IP_tracer/` · **Workflow:** `IPStack Telegram Intelligence Bot.json`

A Telegram bot that turns any IPv4 address into a full OSINT intelligence report using the **IPStack API**. Built on n8n with inline expression-based formatting, parallel enrichment branches, and a weighted risk engine.

### What Is IP Tracing?

IP tracing (IP geolocation + OSINT) is the process of identifying the geographic location, network provider, and security profile of an internet-connected device from its IP address. Every device connected to the internet has a public IPv4 address assigned by its ISP. By querying databases like IPStack, you can determine:

- **Where** the device is located (country, city, coordinates)
- **Who** provides its internet (ISP, organization, ASN)
- **What** type of connection it uses (residential, datacenter, mobile)
- **How risky** it is (proxy, VPN, TOR, crawler detection)

This bot packages all that intelligence into a clean Telegram message with emoji-rich formatting, derived risk scores, and optional weather/sunlight enrichment.

### Architecture

```
Telegram Trigger
    ↓
Switch (regex routing)
    ├── Single IP   → IPStack API → Standard Lookup report
    ├── /myip       → IPStack check → Requester IP Lookup report
    ├── Bulk IPs    → IPStack bulk → Code node → Bulk Lookup report
    └── Invalid     → Sarcastic error reply
```

### 10 Nodes — Zero Parse Nodes

Unlike conventional n8n bots that parse commands in a dedicated Code node, this workflow uses the **Switch node's regex routing** to classify messages directly from the Telegram trigger output:

| Switch Output | Regex | Routes |
|:---:|---|---|
| 0 | Full IPv4 validation (`^(?!(?:0+\.){3}0+)...`) | Single IP lookup |
| 1 | `^\/myip$` | Requester's own IP |
| 2 | IPv4 regex with comma chaining | Bulk lookup (e.g., `8.8.8.8,1.1.1.1`) |
| 3 | `^[\s\S]*$` (catch-all) | Invalid input → error |

### Node Details

| # | Node | Type | Job |
|---|------|------|-----|
| 1 | **Telegram Trigger** | `telegramTrigger` | Webhook listener for `message` updates |
| 2 | **Switch** | `switch` (v3.4) | Regex-based routing to 4 outputs |
| 3 | **Single IP request** | `httpRequest` (v4.4) | `GET https://api.ipstack.com/{ip}?access_key=...` |
| 4 | **User IP request** | `httpRequest` (v4.4) | `GET https://api.ipstack.com/check?access_key=...` |
| 5 | **Bulk IP request** | `httpRequest` (v4.4) | `GET https://api.ipstack.com/{csv}?access_key=...` |
| 6 | **Code in JavaScript** | `code` | Formats bulk response into compact report (170+ lines) |
| 7 | **Requester IP Lookup report** | `telegram` (v1.2) | Sends `/myip` response |
| 8 | **Standard Lookup report** | `telegram` (v1.2) | Sends single IP response |
| 9 | **Bulk Lookup report** | `telegram` (v1.2) | Sends bulk IP response |
| 10 | **Invalid input reply** | `telegram` (v1.2) | Sends sarcastic error + usage |

### Intelligence Signals

Every IPStack response produces a report covering **7 intelligence domains**:

#### Verified (IPStack Telemetry)
- **Network** — IP, hostname, type, ASN, ISP, organization
- **Location** — Country, region, city, ZIP, coordinates, capital
- **Geography** — Continent, flag emoji, calling code, EU membership
- **Time** — Timezone, current time, GMT offset, DST status
- **Economy** — Currency name, code, symbol
- **Language** — Name and native script

#### Derived (Calculated Inline)
- **Speed Class** — Datacenter, Mobile, Cable, DSL, Low
- **Stability** — Fixed routing vs Mobile gateway
- **Profile** — Residential, Mobile, Business, Datacenter detection
- **Hemisphere** — Northern/Southern + Eastern/Western from lat/lon
- **Location Precision** — City+ZIP → High, City-only → Medium, Country-only → Low
- **Period** — Late Night / Morning / Afternoon / Evening / Night
- **Hosting Type** — CDN, Datacenter, Mobile, Residential, General
- **Likely Use Case** — Web Hosting, CDN/VPS, End-User, Home, Server
- **Trust Score** — High (Residential), Medium (Datacenter), Low (Proxy/CDN)
- **Risk Score** — 0–100 weighted from connection + security indicators

#### Enriched (External APIs)
- **Weather** — Temperature, humidity, wind via Open-Meteo (free, no key)
- **Sunrise/Sunset** — Solar times via sunrise-sunset.org (free)

### Key Expression Patterns

| Purpose | Expression |
|---------|-----------|
| Chat ID | `=$('Telegram Trigger').item.json.message.chat.id` |
| IP from message | `=$('Telegram Trigger').item.json.message.text` |
| IPStack field | `={{ JSON.parse($json.data).field }}` |
| Conditional display | `={{ JSON.parse($json.data).field ? "value" : "" }}` |
| Risk badge | `={{ score > 60 ? "🔴 High Risk" : score > 30 ? "🟡 Medium Risk" : "🟢 Low Risk" }}` |

### Setup

#### Prerequisites

| Requirement | Source |
|-------------|--------|
| n8n instance | [n8n.io](https://n8n.io/) or `npx n8n` |
| IPStack API key | [ipstack.com](https://ipstack.com) (free: 100 req/month) |
| Telegram bot token | [@BotFather](https://t.me/botfather) |

#### Steps

1. **Import workflow** — n8n Dashboard → Workflows → Add from file → select `IPStack Telegram Intelligence Bot.json`

2. **Configure Telegram credential** — Settings → Credentials → New → Telegram. Paste your BotFather token. Assign to all 5 Telegram nodes.

3. **Replace API key** — In each HTTP Request node, replace `access_key=your_key_here` with your IPStack key. For production, use `access_key={{ $env.IPSTACK_ACCESS_KEY }}`

4. **Activate** — Toggle the workflow on. Send any IPv4 to your bot.

### Usage

```
Send: 8.8.8.8
  → Full intelligence report: network, location, time, risk, weather

Send: /myip
  → Report on your own public IP

Send: 8.8.8.8,1.1.1.1,9.9.9.9
  → Compact bulk report for up to ~15 IPs

Send: hello
  → Sarcastic error with format instructions
```

### Commands

| Input | What It Does |
|-------|-------------|
| `192.168.1.1` | Single IPv4 lookup with full report |
| `/myip` | Lookup your own public IP |
| `8.8.8.8,1.1.1.1` | Bulk lookup (comma-separated) |
| Anything else | Get roasted + shown correct format |

### Reports

**Single & MyIP** — 6 sections:
1. Header (fancy box with bot branding)
2. VERIFIED — Network, Location, Country, Time, Currency, Language
3. DERIVED — Connection, Profile, Geography, Activity, Risk
4. ENRICHED — Weather + Sun (conditional)
5. SUMMARY — One-liner assessment + Risk badge + Advice + Confidence
6. NOTES — Disclaimers, attribution

**Bulk** — Per-IP compact cards with flag, IP, city, ISP, ASN, coords, risk, precision, hosting type, trust. Truncated at 3500 chars with `"... N more IP(s)"`.

### Known Limitations

- IPStack free tier: 100 req/month. Bulk lookups fail silently beyond quota.
- Telegram 4096 char limit: Bulk reports with >~15 IPs truncated.
- Mobile IPs resolve to carrier gateways, anycast IPs to nearest POP.
- API key hardcoded in JSON export — use env vars for production.
- No caching — every request triggers fresh API call.
- No input sanitization beyond regex — large payloads may hit n8n limits.

### Files

| File | Purpose |
|------|---------|
| `IPStack Telegram Intelligence Bot.json` | Exported n8n workflow (import this) |
| `IMPLEMENTATION.md` | Architecture deep-dive |
| `RESEARCH_DONE.md` | Full research paper on IP intelligence |
| `RESEARCH_DONE.pdf` | Research in PDF format |
| `formatter.js` | Legacy formatter (previous architecture) |
| `message_template.txt` | Standard Lookup report template |
| `myip_template.txt` | MyIP report template |
| `bulk_template.txt` | Bulk Code node template |

---

## Getting Started (Common)

### Prerequisites

```bash
# Install n8n globally
npm install -g n8n

# Verify Python 3
python --version

# Install Cloudflare Tunnel
# Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
cloudflared --version
```

### Launcher Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| `start_n8n.py` | Repository root | Single-project launcher (configurable) |
| `start_all_projects.py` | Repository root | Multi-project launcher with webhook refresh |

Both scripts handle: Cloudflare Tunnel startup → URL extraction → env var setup → n8n launch.

---

## Repository Structure

```
n8n-projects/
├── README.md                         ← You are here
├── start_n8n.py                      ← Single-project launcher
├── start_all_projects.py             ← Multi-project launcher
│
├── QR_code_generator/                ← QR Code Generator Bot
│   ├── Telegram bot - QR code generator.json
│   ├── RUN_CONFIG_AUTO.py
│   ├── CONFIG.MD                     (legacy ngrok guide)
│   ├── images/                       (screenshots + diagrams)
│   ├── linkedinPost.txt             (local only)
│   └── linkedin_banner.png          (local only)
│
└── IP_tracer/                        ← TracedIP Intelligence Bot
    ├── IPStack Telegram Intelligence Bot.json
    ├── IMPLEMENTATION.md
    ├── RESEARCH_DONE.md
    ├── RESEARCH_DONE.pdf
    ├── formatter.js
    ├── message_template.txt
    ├── myip_template.txt
    ├── bulk_template.txt
    ├── linkedinPost.txt             (local only)
    └── linkedin_banner.png          (local only)
```

---

## Author

**Nitin Kumar** · [LinkedIn](https://www.linkedin.com/in/nitin30kumar/) · [GitHub](https://github.com/nitinkumar30)

Built on evenings and weekends when we should have been sleeping.
