# n8n Projects 🤖⚙️

This folder contains **n8n automation projects** (exported workflows). Import them into n8n, run them, and pretend you planned it all from scratch. 😄

---

## Why n8n? (aka “because life is too short”) ⏱️

n8n is important because it turns repetitive tasks into **automated flows**—and it does it without requiring you to build an entire backend.

Everyday “this could be automated” wins:

- 🔔 **Telegram messages → actions** (reply, validate, fetch info, notify)
- 🌐 **Text → something useful** (QR codes, summaries, transformations)
- 📄 **Move data between services** (HTTP APIs → Sheets/DB → alerts)
- 🧠 **Validation & branching** (stop garbage inputs before they reach APIs)
- 🧩 **Glue everything together** (webhooks, REST calls, retries, routing)

Sarcastic truth: if something can be triggered, it can probably be automated. n8n just makes it less painful. 😌

---

## What is n8n? 🧱

**n8n** is an open-source workflow automation tool. It connects:

- **Triggers** (events) 
- **Nodes** (logic/actions)
- **Outputs** (results back to users/services)

Using a visual builder, so you can focus on outcomes instead of copy/pasting HTTP requests 400 times.

---

## Quick Telegram setup note 📣 (webhooks require HTTPS)

If a workflow uses **Telegram**, you usually cannot rely on `localhost` over plain `http://`.

Telegram expects a **public HTTPS webhook**. Typical approach:

- Run n8n locally 🖥️
- Expose it using **ngrok** 🌍🔒

Then set these env vars **before starting n8n**:

- `WEBHOOK_URL` = `https://<your-ngrok-host>`
- `N8N_PROTOCOL` = `https`
- `N8N_HOST` = `<your-ngrok-host>` (no `https://`)

Example (PowerShell):

```powershell
$env:WEBHOOK_URL="https://your-subdomain.ngrok-free.app"
$env:N8N_PROTOCOL="https"
$env:N8N_HOST="your-subdomain.ngrok-free.app"
```

After changing env vars, **restart n8n**. Telegram is picky; n8n is obedient.

---

## Projects 📂

| Project | What it does 🤳 | Trigger | Output ✅ | Files to look at |
|---|---|---|---|---|
| **QR_code_generator** | Telegram bot that accepts a URL/text, validates it, generates a QR code via an API, and sends the QR image back to the user. 📷 | Telegram Trigger (On Message) | Telegram photo message (QR image) | `n8n-projects/QR_code_generator/README.MD` + `Telegram bot - QR code generator.json` |

---

## Importing workflows into n8n 🧰

Most projects include an exported workflow JSON file.

General steps:

1. Start n8n
2. In n8n UI → **Workflows** → **Import from file**
3. Select the workflow JSON from the project folder
4. Configure credentials (e.g., Telegram Bot Token) inside n8n
5. Enable the workflow and test

Tip: Keep the workflow JSON close to its project README so setup steps stay readable. ✅

---

## Security notes 🔐

- Keep your **Telegram Bot Token** private 🔒
- Don’t commit secrets into git/repo
- Use n8n credentials management for tokens and API keys

---

## Author 👨‍💻

[Nitin Kumar](https://www.linkedin.com/in/nitin30kumar/)

