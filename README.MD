# n8n Mini Projects

[![n8n](https://img.shields.io/badge/engine-n8n-%23EA4AAA?style=flat-square&logo=n8n)](https://n8n.io)
[![Telegram](https://img.shields.io/badge/chat-Telegram-%2326A5E4?style=flat-square&logo=telegram)](https://core.telegram.org/bots/api)
[![Cloudflare](https://img.shields.io/badge/tunnel-Cloudflare-F38020?style=flat-square&logo=cloudflare)](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success?style=flat-square)](#)

A growing collection of **n8n-based mini projects** — mostly Telegram bots that run locally, exposed via Cloudflare Tunnel for free HTTPS. Each project includes its workflow JSON, setup guide, and any associated scripts.

---

## Project Catalog

| Project | Description | Nodes | Key API | Folder |
|---------|-------------|-------|---------|--------|
| [QR Code Generator Bot](QR_code_generator/README.MD) | Generate QR codes from any URL via Telegram | 4 | QRServer API | `QR_code_generator/` |
| [TracedIP Intelligence Bot](IP_tracer/README.md) | Full OSINT IP lookup with risk scoring | 10 | IPStack API | `IP_tracer/` |

> Click project names for detailed documentation.

---

## Prerequisites

| Tool | Install Command / Link | Purpose |
|------|----------------------|---------|
| **Node.js** | [nodejs.org](https://nodejs.org/) | Runtime for n8n |
| **n8n** | `npm install -g n8n` | Workflow automation engine |
| **Python 3** | [python.org](https://python.org/) | Launcher & automation scripts |
| **Cloudflared** | [developers.cloudflare.com](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) | Free HTTPS tunnel |
| **Git** | [git-scm.com](https://git-scm.com/) | Version control |
| **Telegram Bot Token** | Via [@BotFather](https://t.me/botfather) | Bot authentication |

Verify everything:

```bash
node -v && npm -v
n8n --version
python --version
cloudflared --version
git --version
```

---

## Major Steps to Start Building

1. **Set up n8n** — Install globally, run `n8n start`, open `http://localhost:5678`
2. **Create a Telegram bot** — Use BotFather (see guide below) and save the token
3. **Design the workflow** — Add Telegram Trigger → logic nodes → action nodes → response
4. **Test locally** — Use n8n's Test mode to verify each node
5. **Activate** — Switch to ACTIVE mode for 24/7 listening
6. **Expose via tunnel** — Run cloudflared so Telegram can reach your webhook

---

## How to Create a Bot Using BotFather

1. Open [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow the prompts:
   - Enter a **name** for your bot (e.g., `My Awesome Bot`)
   - Enter a **username** ending in `bot` (e.g., `my_awesome_bot`)
4. BotFather replies with a **bot token** — copy and save it immediately
5. (Optional) Customize with:
   - `/setdescription` — what the bot does
   - `/setcommands` — list of available commands
   - `/setuserpic` — profile picture

The token is used in n8n's Telegram credential configuration.

---

## Debugging in n8n

### Common Node Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Telegram Trigger not firing | Workflow not ACTIVE | Click ACTIVE (top-right), not Test |
| Webhook error (HTTPS) | No tunnel running | Start cloudflared or ngrok |
| "Test Workflow" only runs once | Test mode is ephemeral | Use ACTIVE for production |
| Credential error (401) | Wrong bot token | Re-create token in BotFather |
| HTTP Request fails | API key missing / wrong URL | Check the URL and credentials |

### Debugging Tips

- **Add a Code node** with `console.log($json)` to inspect data flowing between nodes
- **Use the n8n console** — check the terminal where n8n is running for error logs
- **Isolate branches** — temporarily disconnect nodes to narrow down failures
- **Check execution order** — n8n v1 vs v2 execution order can cause timing issues
- **Expression tester** — use `{{ }}` in n8n's UI to test expressions before building your template

---

## Major Uses of n8n in Automation

- **Telegram bots** — chatbots, notification systems, command handlers
- **Webhook processing** — receive data from any service and transform it
- **API orchestration** — chain multiple APIs with data transformation between them
- **Data ETL** — extract, transform, load from databases, sheets, files, APIs
- **Monitoring & alerts** — poll endpoints, check conditions, send notifications
- **Social media automation** — cross-post, schedule, aggregate content
- **File processing** — convert, resize, watermark images; parse CSV/Excel
- **Email automation** — send/receive emails, parse attachments, trigger workflows
- **Database operations** — CRUD on PostgreSQL, MySQL, MongoDB, etc.
- **Scheduled tasks** — cron-like triggers for periodic jobs

---

## Git Commands (Frequent Push Workflow)

```bash
# Check what changed
git status

# Stage all changes (careful: use .gitignore to exclude secrets)
git add .

# Commit with a descriptive message
git commit -m "Describe what you changed"

# Push to GitHub
git push

# Full flow in one shot
git add . && git commit -m "Update" && git push
```

### Common Patterns

```bash
# Push a new project
git add QR_code_generator/            # stage specific folder
git commit -m "Add QR bot workflow"
git push

# Undo staging a file
git restore --staged unwanted_file.json

# Check remote URL
git remote -v
```

---

## How to Efficiently Run These Projects

### Single Project

```bash
python start_n8n.py
```

Starts Cloudflare Tunnel + n8n, extracts the HTTPS URL, and keeps everything running.

### All Projects (Multi-Project Mode)

```bash
python start_all_projects.py
```

Runs one n8n instance with one tunnel, then refreshes webhooks for all active projects.

### Manual Steps

1. Start cloudflared: `cloudflared tunnel --url http://localhost:5678`
2. Copy the HTTPS URL from the output
3. Set env vars: `WEBHOOK_URL`, `N8N_PROTOCOL=https`, `N8N_HOST=<url>`
4. Start n8n: `n8n start`

### Project-Specific Scripts

Each project folder may contain its own launcher. Refer to the project's README for details.

---

## Repository Structure

```
n8n-projects/
├── README.MD                    ← You are here
├── start_n8n.py                 ← Single-project launcher
├── start_all_projects.py        ← Multi-project launcher
├── README_OLD.MD                ← Previous root README (archive)
│
├── QR_code_generator/           ← QR Code Generator Bot
├── IP_tracer/                   ← TracedIP Intelligence Bot
└── ... (more projects added here)
```

Each project folder contains:
- **Workflow JSON** — import directly into n8n
- **README.MD** — project-specific documentation
- **Supporting files** — images, scripts, templates

---

## Author

**Nitin Kumar** · [LinkedIn](https://www.linkedin.com/in/nitin30kumar/) · [GitHub](https://github.com/nitinkumar30)
