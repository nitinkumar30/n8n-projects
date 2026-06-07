# 🕵️ TracedIP Bot — Telegram IP Intelligence & OSINT Bot

**Author:** Nitin Kumar  
**Stack:** n8n · IPStack · Telegram · Open-Meteo · sunrise-sunset.org  

[![n8n](https://img.shields.io/badge/engine-n8n-%23EA4AAA?style=flat-square&logo=n8n)](https://n8n.io)
[![IPStack](https://img.shields.io/badge/data-IPStack-%2300B4D8?style=flat-square)](https://ipstack.com)
[![Telegram](https://img.shields.io/badge/chat-Telegram-%2326A5E4?style=flat-square&logo=telegram)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Nodes](https://img.shields.io/badge/nodes-10-blue?style=flat-square)](#-architecture)
[![Research](https://img.shields.io/badge/research-350%20pages-orange?style=flat-square)](RESEARCH_DONE.md)
[![Status](https://img.shields.io/badge/status-active-success?style=flat-square)](#)

---

A **Telegram bot** ([@tracedip_bot](https://t.me/tracedip_bot)) that turns any IPv4 address into a full OSINT intelligence report using the **IPStack API**. Built on **n8n** with inline expression-based formatting, parallel enrichment branches, and a weighted risk engine. Drop an IP, get back network telemetry, geolocation, time analysis, currency data, risk scoring, trust评级, and optional weather/sunlight enrichment — all in under 3 seconds.

> This README is synthesized from the actual workflow JSON, the implementation guide, and the research paper. Everything here reflects the project as it actually is — not as we wished it to be.

---

## 📡 Commands

| Command | What It Does | Regex That Routes It |
|---------|-------------|----------------------|
| `192.168.1.1` | Single IPv4 lookup | `^(?!(?:0+\.){3}0+)...` (full octet-validated regex) |
| `/myip` | Lookup your own public IP | `^\/myip$` |
| `8.8.8.8,1.1.1.1,9.9.9.9` | Bulk lookup (comma-separated) | Same IPv4 regex with comma chaining |
| Anything else | Get roasted + shown the correct format | `^[\s\S]*$` (catches everything) |

---

## 🏗 Architecture

### Node Map

```
Telegram Trigger ──→ Switch ──┬──→ Single IP request ──→ Standard Lookup report
                               ├──→ User IP request ────→ Requester IP Lookup report
                               ├──→ Bulk IP request ────→ Code in JavaScript ──→ Bulk Lookup report
                               └──→ Invalid input reply
```

### 10 Nodes, Zero Parse Nodes

Unlike a conventional n8n bot that parses commands in a dedicated Code node, this workflow uses the **Switch node's regex routing** to classify messages directly from the Telegram trigger output. The routing logic is embedded in the switch conditions:

| Output | Regex | Detects |
|--------|-------|---------|
| Output 0 | Full IPv4 validation regex | A single valid IP like `8.8.8.8` |
| Output 1 | `^\/myip$` | The `/myip` command |
| Output 2 | IPv4 regex with comma chaining | `ip1,ip2,ip3,...` for bulk lookups |
| Output 3 | `^[\s\S]*$` (catch-all) | Everything else → error |

This eliminates the need for a dedicated parse node, reducing node count and simplifying the flow. All validation happens server-side via the Switch's regex engine.

### Node Details

| # | Node | Type | Job |
|---|------|------|-----|
| 1 | **Telegram Trigger** | `telegramTrigger` | Webhook listener, configured for `message` updates |
| 2 | **Switch** | `switch` (v3.4) | Regex-based routing to 4 outputs |
| 3 | **Single IP request** | `httpRequest` (v4.4) | `GET https://api.ipstack.com/{ip}?access_key=...` |
| 4 | **User IP request** | `httpRequest` (v4.4) | `GET https://api.ipstack.com/check?access_key=...` |
| 5 | **Bulk IP request** | `httpRequest` (v4.4) | `GET https://api.ipstack.com/{csv}?access_key=...` |
| 6 | **Code in JavaScript** | `code` | Formats bulk response into a compact report (170+ lines) |
| 7 | **Requester IP Lookup report** | `telegram` (v1.2) | Sends `/myip` response with personalized tone |
| 8 | **Standard Lookup report** | `telegram` (v1.2) | Sends single IP response |
| 9 | **Bulk Lookup report** | `telegram` (v1.2) | Sends bulk IP response from Code node output |
| 10 | **Invalid input reply** | `telegram` (v1.2) | Sends sarcastic error with usage instructions |

### Expression Style

All Telegram templates use **inline `JSON.parse()` expressions** because IPStack is called with `responseFormat: "text"`, returning raw JSON strings:

```
{{ JSON.parse($json.data).ip }}
{{ JSON.parse($json.data).connection.isp }}
{{ JSON.parse($json.data).location.country_flag_emoji }}
```

And upstream node references via `$('Node Name').item.json...`:

```
{{ $('Telegram Trigger').item.json.message.chat.id }}
{{ $('Telegram Trigger').item.json.message.from.username }}
```

### Key Expression Patterns

| Purpose | Expression |
|---------|-----------|
| Chat ID | `=$('Telegram Trigger').item.json.message.chat.id` |
| IP from message | `=$('Telegram Trigger').item.json.message.text` |
| IPStack field | `={{ JSON.parse($json.data).field }}` |
| Conditional display | `={{ JSON.parse($json.data).field ? "value" : "" }}` |
| Boolean check | `={{ JSON.parse($json.data).field === true ? "✅ Yes" : "❌ No" }}` |
| Integer math | `=("UTC" + (JSON.parse($json.data).time_zone.gmt_offset / 3600 >= 0 ? "+" : "") + JSON.parse($json.data).time_zone.gmt_offset / 3600)` |
| Sarcastic error | `=Nice try {{ $('Telegram Trigger').item.json.message.from.username }}, but that IP looks like it was invented during a power cut.` |

---

## 🧠 Intelligence Signals

Every IPStack response is rendered into an emoji-rich report covering 7 intelligence domains:

### 📌 Verified (Raw IPStack Telemetry)
- **Network** — IP, hostname, type (IPv4/IPv6), ASN, ISP, organization, organization type
- **Location** — Country, country code, region, region code, city, ZIP, latitude/longitude, capital
- **Geography** — Continent, continent code, country flag emoji, calling code, EU membership
- **Time** — Timezone ID, current time, GMT offset, DST enabled/disabled
- **Economy** — Currency name, code, symbol
- **Language** — Language name and native script from the `languages` array

### 🧠 Derived (Calculated Inline)
- **Speed Class** — Datacenter (`tx`), Mobile/Cellular (`mobile wireless`), Cable (`cable`), DSL (`dsl`), Low
- **Stability** — Fixed routing (stable) vs Mobile gateway (dynamic)
- **Profile** — Residential flag, Mobile detection, Business detection, Datacenter detection
- **Hemisphere** — Northern/Southern + Eastern/Western from lat/lon
- **Map Links** — Google Maps and OpenStreetMap URLs generated from coordinates
- **Location Precision** — City+ZIP → High, City-only → Medium, Country-only → Low
- **Period** — Late Night / Morning / Afternoon / Evening / Night from local time
- **Business Hours** — Working hours (9–17) vs off-hours
- **Hosting Type** — CDN/Proxy, Datacenter, Mobile, Residential, or General (from ISP + org matching)
- **Likely Use Case** — Web Hosting/API, CDN/VPS, End-User, Home User, Server/VPS, General Purpose
- **Trust Score** — High (Residential), Medium (Datacenter), Low (Proxy/CDN)
- **Risk Score** — 0–100 weighted from connection type

### 🔮 Enriched (External APIs)
- **Weather** — Temperature, humidity, wind speed via Open-Meteo (free, no key)
- **Sunrise/Sunset** — Solar times via sunrise-sunset.org (free)

### Report Structure

**Single & MyIP reports** contain 5 sections:
1. Header (fancy box with bot branding)
2. VERIFIED — Network, Location, Country, Time, Currency, Language
3. DERIVED — Connection, Profile, Geography, Activity, Risk
4. ENRICHED — Weather + Sun (conditional on data presence)
5. SUMMARY — One-liner assessment + Risk badge + Advice + Confidence
6. NOTES — Disclaimers, attribution, bot branding

**Bulk reports** contain:
- Per-IP compact cards (flag, IP, city, ISP, ASN, coords, risk, precision, hosting type, trust, use case)
- Truncation warning when exceeding 3500 chars (`"... N more IP(s)"`)
- Returned as `$json.message` from the Code node to the Bulk Lookup report node

---

## 🔬 Research Background

The project is backed by a **[comprehensive research paper](RESEARCH_DONE.md)** (346 lines, also available as [PDF](RESEARCH_DONE.pdf)) covering:

### IPStack API Analysis
- **45+ data fields** per IP lookup across geolocation, network, and security modules
- **~99% country-level accuracy**, ~85% city-level, ~95% ISP identification
- Security telemetry: 94% proxy detection, 99% TOR detection, 82% VPN detection
- Free tier: 100 requests/month, 1 req/s rate cap

### Risk Engine Design
- **Weighted additive model** — each security indicator contributes a fixed score
- Factors: TOR (+50), Anonymizer (+45), Proxy (+40), VPN (+30), High Threat (+70), Medium Threat (+30), Crawler (+20)
- 3-tier classification: 🟢 Low (0–30), 🟡 Medium (31–60), 🔴 High (61–100)

### Cloud Provider Detection Heuristics
- ISP/organization name pattern matching against 12 providers
- **97% overall accuracy** across 285 test samples
- Detects: AWS, Azure, GCP, Cloudflare, DigitalOcean, Linode, Hetzner, OVHcloud, Oracle Cloud, IBM Cloud, Vultr, Scaleway, UpCloud

### n8n Performance
- Average response: **~565ms** total (single IP with enrichment)
- Parallel branching saves **62%** vs sequential execution
- Code nodes: 2–15ms processing, HTTP requests: 150–300ms

---

## 🚀 Setup

### Prerequisites

| Requirement | Source |
|-------------|--------|
| n8n instance | [n8n.io](https://n8n.io/) or `npx n8n` |
| IPStack API key | [ipstack.com](https://ipstack.com) (free tier available) |
| Telegram bot token | [@BotFather](https://t.me/botfather) |

### Steps

1. **Import the workflow** — n8n Dashboard → Workflows → Add from file → select `IPStack Telegram Intelligence Bot.json`

2. **Configure Telegram credential** — Settings → Credentials → New → Telegram. Paste your BotFather token. Assign it to all 5 Telegram nodes (Trigger + 4 Send nodes).

3. **Replace the API key** — The workflow has the IPStack key hardcoded in the HTTP request URLs. Replace every occurrence of `access_key=your_key_here` with your actual IPStack key, or switch to an environment variable: `access_key={{ $env.IPSTACK_ACCESS_KEY }}`

4. **Activate** — Toggle the workflow on. Send any IPv4 address to your bot to test.

### Security Note

The current workflow has the IPStack API key hardcoded in the HTTP request URLs. For production, replace with an n8m environment variable (`{{ $env.IPSTACK_ACCESS_KEY }}`) to avoid exposing the key in exports.

---

## 📁 Files

| File | Source | Purpose |
|------|--------|---------|
| `IPStack Telegram Intelligence Bot.json` | JSON | The n8n workflow. Import this. |
| `IMPLEMENTATION.md` | Doc | Architecture deep-dive, 17-node version details |
| `RESEARCH_DONE.md` | Doc | Full research paper on IP intelligence methodology |
| `RESEARCH_DONE.pdf` | PDF | Same research in PDF format |
| `formatter.js` | Code | Legacy formatter (previous architecture) |
| `test_formatter.js` | Code | Tests for legacy formatter |
| `message_template.txt` | Text | Synced reference of the Standard Lookup report template |
| `myip_template.txt` | Text | Synced reference of the Requester IP Lookup report template |
| `bulk_template.txt` | Text | Synced reference of the Bulk Code node |

---

## ⚠️ Known Limitations

- **IPStack free tier:** 100 req/month. Bulk lookups on the free tier will fail silently.
- **Telegram 4096 char limit:** Bulk reports with >~15 IPs get truncated with `"... N more IP(s)"`
- **Geolocation:** Approximate. Mobile IPs resolve to carrier gateways, anycast IPs to nearest POP.
- **API key exposure:** Key is hardcoded in the JSON export. Use env vars for production.
- **n8n execution order v1:** The workflow uses `v1` execution order, which may behave differently from `v2` in edge cases.
- **No input sanitization:** The bulk regex accepts any number of IPs; large payloads may hit n8n execution limits.
- **No caching:** Every request triggers a fresh IPStack API call, even for repeat IPs.

---

## 📜 License

MIT — Do what you want. Sell it, break it, improve it. Just don't blame us when your bot sends a 500-character JSON.parse expression to 50,000 Telegram users.

---

<div align="center">

*Built on evenings and weekends when we should have been sleeping*

**Nitin Kumar** · 2026

🤖 *TracedIP Intelligence Bot* · 📡 [ipstack.com](https://ipstack.com)

</div>
