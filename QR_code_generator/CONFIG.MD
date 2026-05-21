# 🧠 Full Setup Guide (n8n + Telegram + ngrok + HTTPS Fix)

This guide assumes you are running **n8n locally on Windows** and want Telegram Trigger to work properly.

---

# ⚠️ Why this setup is needed (important)

Telegram bots **DO NOT work with localhost or HTTP**.

They require:

```txt id="t1"
https://public-domain.com/webhook
```

So we use:

* 🧩 n8n → automation engine
* 🌍 ngrok → exposes localhost as HTTPS
* 🤖 Telegram → sends webhook updates to n8n

---

# 🧰 STEP 1 — Install everything

## 1. Install n8n

If using Node.js:

```bash id="n2"
npm install -g n8n
```

Run later with:

```bash id="n3"
n8n start
```

---

## 2. Install ngrok

Download:
[https://ngrok.com/download](https://ngrok.com/download)

Then authenticate:

```bash id="n4"
ngrok config add-authtoken YOUR_TOKEN
```

---

# 🚀 STEP 2 — Start n8n (DO NOT SKIP THIS PART)

Open **PowerShell as Administrator**

Go to your project (optional):

```powershell id="p1"
cd Desktop
```

---

## 🧠 Set REQUIRED environment variables

This is the MOST IMPORTANT part.

Run this in PowerShell:

```powershell id="p2"
$env:WEBHOOK_URL="https://your-ngrok-url.ngrok-free.app"
$env:N8N_PROTOCOL="https"
$env:N8N_HOST="your-ngrok-url.ngrok-free.app"
```

### ⚠️ Important rules:

* ❌ Do NOT include `http://`
* ❌ Do NOT include trailing `/`
* ✔ Only raw domain for HOST
* ✔ Full https URL for WEBHOOK_URL

---

## ▶️ Now start n8n in SAME terminal

```powershell id="p3"
n8n start
```

Keep this terminal open.

---

# 🌍 STEP 3 — Start ngrok (SECOND terminal)

Open another PowerShell window:

```bash id="p4"
ngrok http 5678
```

You will see:

```txt id="p5"
Forwarding  https://abcd1234.ngrok-free.app -> http://localhost:5678
```

---

## 📌 COPY THIS URL:

```txt id="p6"
https://abcd1234.ngrok-free.app
```

---

# 🔁 STEP 4 — RESTART n8n with correct URL (IMPORTANT)

Now go back to first PowerShell and STOP n8n (CTRL + C).

Then update variables again:

```powershell id="p7"
$env:WEBHOOK_URL="https://abcd1234.ngrok-free.app"
$env:N8N_PROTOCOL="https"
$env:N8N_HOST="abcd1234.ngrok-free.app"
```

Now start again:

```powershell id="p8"
n8n start
```

---

# 🤖 STEP 5 — Configure Telegram correctly

## 1. Create bot

Use:

👉 [https://t.me/BotFather](https://t.me/BotFather)

Command:

```txt id="t2"
/newbot
```

Get:

```txt id="t3"
BOT TOKEN
```

---

## 2. Add Telegram Trigger in n8n

Select:

* Node: **Telegram Trigger**
* Event: **On Message**
* Paste Bot Token

---

# ⚠️ If webhook error appears

If you see:

```txt id="t4"
Bad webhook: HTTPS required
```

Then:

✔ ngrok is not running
✔ OR WEBHOOK_URL is wrong
✔ OR n8n was not restarted after setting env vars

---

# 🔍 STEP 6 — Verify webhook is correct

Open browser:

```txt id="t5"
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

You should see:

```json id="t6"
"url": "https://abcd1234.ngrok-free.app/webhook/..."
```

If not → setup is still wrong.

---

# 🧩 STEP 7 — Final working architecture

```txt id="a1"
Telegram User
     ↓
Telegram Trigger (via HTTPS webhook)
     ↓
n8n Workflow
     ↓
QR API
     ↓
Telegram Send Photo
```

---

# 🧠 COMMON MISTAKES (very important)

## ❌ Mistake 1

Using localhost in webhook

✔ Fix:
Always use ngrok HTTPS URL

---

## ❌ Mistake 2

Not restarting n8n after env change

✔ Fix:
You MUST restart n8n every time

---

## ❌ Mistake 3

Putting http instead of https

✔ Fix:
Telegram only accepts HTTPS

---

## ❌ Mistake 4

Wrong N8N_HOST format

✔ Fix:

```txt id="h1"
abcd1234.ngrok-free.app   ✔
https://abcd1234...        ❌
```

---

# 🚀 BONUS — one-command setup (clean version)

If you want clean restart flow:

### Terminal 1:

```bash id="b1"
ngrok http 5678
```

### Terminal 2:

```powershell id="b2"
$env:WEBHOOK_URL="https://abcd1234.ngrok-free.app"
$env:N8N_PROTOCOL="https"
$env:N8N_HOST="abcd1234.ngrok-free.app"
n8n start
```

---

# 🎯 RESULT

After this setup:

* Telegram Trigger works instantly
* No webhook errors
* QR bot runs smoothly
* Fully local + public HTTPS bridge

## Author

[Nitin Kumar](https://www.linkedin.com/in/nitin30kumar/)