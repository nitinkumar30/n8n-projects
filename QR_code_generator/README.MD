# 🫡✨ QR Code Generator Bot (n8n + Telegram) — now with Cloudflare Tunnel

![Gemini_Generated_Image_ev6otpev6otpev6o](./images/Gemini_Generated_Image_ev6otpev6otpev6o.png)


This folder contains a Telegram bot workflow built in **n8n** that:

- ✅ accepts a URL/text from a Telegram chat
- ✅ validates it (so random nonsense doesn’t hit the QR API)
- ✅ generates a QR code via **QRServer**
- ✅ sends the QR image back to the user
- ✅ runs continuously on your machine (while your PC is ON) 🤖

And—most importantly—your webhook runs over **FREE HTTPS using Cloudflare Tunnel**, so you don’t have to reconfigure ngrok every 5 minutes. (ngrok, we hardly knew ye. 😭)

---

## 📌 What’s new in this implementation (vs the older ngrok-based approach)

- 🌐 **Replaced ngrok** with **Cloudflare Tunnel (cloudflared)**
- 🧠 **Added an auto-start Python runner** that:
  - starts Cloudflare Tunnel
  - parses the created public HTTPS URL
  - sets `WEBHOOK_URL`, `N8N_PROTOCOL`, `N8N_HOST` automatically
  - starts `n8n`
- ♾️ **Emphasized Active mode workflow** (continuous listening)
- 🧯 Documented common failure cases: test vs active mode, webhook HTTPS issues, etc.

---

## 🧩 Tech stack

| Tool | Purpose |
|---|---|
| **n8n** | Workflow automation engine |
| **Telegram Bot API** | Receive messages + send QR images |
| **Cloudflare Tunnel** | Public HTTPS tunnel for your local webhook |
| **QRServer API** | Generates the QR image |
| **Python** | Auto-start script (starts tunnel + sets env vars + starts n8n) |

---

## 🔧 Final architecture

```txt
Telegram User
   ↓
Telegram Servers
   ↓
Cloudflare HTTPS Tunnel
   ↓
Local n8n instance (webhook)
   ↓
QR Generation workflow
   ↓
Telegram Send Photo (QR image)
```

---

## 🚀 Option A: Run with Cloudflare Tunnel (recommended)

### Prerequisites

1) Install Node.js + n8n

```bash
npm install -g n8n
```

2) Install Python (and add to PATH)

Verify:

```bash
python --version
```

3) Install Cloudflare Tunnel (cloudflared)

Verify:

```bash
cloudflared --version
```

### Run

Use the root launcher:

```bash
python ../start_n8n.py
```

### Important

- In n8n, ensure the workflow is set to **ACTIVE** (not "Test").

---

## 🧾 Files in this folder

- `Telegram bot - QR code generator.json` → the exported n8n workflow to import
- `images/` → screenshots and diagrams

---

## 👨‍💻 Author

[Nitin Kumar](https://www.linkedin.com/in/nitin30kumar/)

