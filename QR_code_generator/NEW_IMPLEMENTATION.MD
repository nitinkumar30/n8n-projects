# 🤖⚡ Telegram QR Code Generator Bot (n8n + Cloudflare Tunnel)

A fully automated Telegram bot that:
 
✅ Accepts URLs from users  
✅ Validates links  
✅ Generates QR codes instantly  
✅ Sends QR image back to Telegram  
✅ Runs continuously on your local machine  
✅ Uses FREE HTTPS via Cloudflare Tunnel  
✅ No ngrok pain anymore 😌  

---

# 🧠 What This Project Actually Does

User sends:

```txt
https://google.com
````

Bot replies with:

📦 QR Code Image

Simple. Fast. Weirdly satisfying.

---

# 🚀 Tech Stack

| Tool              | Purpose                      |
| ----------------- | ---------------------------- |
| n8n               | Workflow automation          |
| Telegram Bot API  | Messaging platform           |
| Cloudflare Tunnel | FREE HTTPS public tunnel     |
| QRServer API      | QR code generation           |
| Python            | Auto-start automation script |

---

# 🏗️ Final Architecture

```txt
Telegram User
      ↓
Telegram Servers
      ↓
Cloudflare HTTPS Tunnel
      ↓
Local n8n Instance
      ↓
QR Generation Workflow
      ↓
Telegram Bot Response
```

---

# ❌ Why We Removed ngrok

Initially, ngrok was used for HTTPS webhooks.

But free ngrok had problems:

❌ URL changes constantly
❌ Manual restart needed
❌ Reconfigure environment variables every time
❌ Emotional damage

So we replaced it with:

# ✅ Cloudflare Tunnel

Benefits:

✅ Completely FREE
✅ Stable HTTPS tunnel
✅ Faster startup
✅ Easier automation
✅ Better long-running setup
✅ No auth token headache

---

# 🎯 Features

✅ Telegram bot integration
✅ URL validation using regex
✅ Automatic QR generation
✅ Continuous webhook listening
✅ Automatic HTTPS setup
✅ Auto-start script
✅ Infinite trigger execution (while PC stays ON)

---

# 📦 Project Workflow

```txt
Telegram Trigger
      ↓
IF URL VALID?
   ↓ YES       ↓ NO
Generate QR    Send Error
      ↓
Send Photo
```

---

# 🛠️ Installation Guide

---

# 1️⃣ Install Node.js

Download:

[https://nodejs.org/](https://nodejs.org/)

Verify:

```bash
node -v
npm -v
```

---

# 2️⃣ Install n8n

Open PowerShell:

```bash
npm install -g n8n
```

Verify:

```bash
n8n --version
```

---

# 3️⃣ Install Python

Download:

[https://www.python.org/downloads/](https://www.python.org/downloads/)

IMPORTANT:

✅ Enable:

```txt
Add Python to PATH
```

Verify:

```bash
python --version
```

---

# 4️⃣ Install Cloudflare Tunnel

Download:

[https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)

Verify:

```bash
cloudflared --version
```

---

# 🤖 Telegram Bot Setup

Open:

👉 [https://t.me/BotFather](https://t.me/BotFather)

Create bot:

```txt
/newbot
```

You’ll receive:

```txt
BOT TOKEN
```

Save it carefully 🔑

---

# 🧩 n8n Workflow Setup

Open n8n:

```txt
http://localhost:5678
```

---

# 🔹 Node 1 — Telegram Trigger

Select:

```txt
Telegram Trigger
```

Event:

```txt
On Message
```

Paste Telegram Bot Token.

---

# 🔹 Node 2 — IF Node (URL Validation)

Condition:

```javascript
{{$json["message"]["text"]}}
```

Regex:

```regex
^(https?:\/\/)[^\s]+$
```

This blocks:

* random text
* invalid URLs
* chaos

Because users are creative in dangerous ways.

---

# 🔹 Node 3 — HTTP Request (QR Generator)

URL:

```txt
=https://api.qrserver.com/v1/create-qr-code/?data={{encodeURIComponent($json["message"]["text"])}}&size=350x350&ecc=M&color=1a73e8&bgcolor=ffffff&qzone=4&margin=10&format=png
```

This generates:

* styled QR
* proper spacing
* better readability

---

# 🔹 Node 4 — Telegram Send Photo

Chat ID:

```javascript
{{$node["Telegram Trigger"].json["message"]["chat"]["id"]}}
```

Binary Property:

```txt
data
```

Caption:

```txt
Here is your QR code 😌
```

---

# 🧠 IMPORTANT — Test Mode vs Active Mode

This is where many people suffer.

---

# ❌ Test Workflow

Runs ONCE only.

Used for:

* debugging
* development

After first execution:

```txt
listener stops
```

---

# ✅ Active Workflow

Runs continuously forever.

Used for:

* real Telegram bots
* production usage

---

# 🚀 How To Run Continuously

Just ensure:

| Requirement           | Needed? |
| --------------------- | ------- |
| PC ON                 | ✅       |
| Internet ON           | ✅       |
| Python script running | ✅       |
| Workflow ACTIVE       | ✅       |

That’s it.

---

# 🐍 Automatic Startup Script

Create:

```txt
start_n8n.py
```

Paste:

```python
import subprocess
import threading
import re
import os
import time

cloudflare_url = None

print("🚀 Starting Cloudflare Tunnel...\n")

cf_process = subprocess.Popen(
    ["cloudflared", "tunnel", "--url", "http://localhost:5678"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

def read_cloudflare_logs():
    global cloudflare_url

    for line in cf_process.stdout:
        print(line.strip())

        match = re.search(
            r"https://[-a-zA-Z0-9]+\.trycloudflare\.com",
            line
        )

        if match and cloudflare_url is None:
            cloudflare_url = match.group(0)
            print(f"\n✅ URL Found: {cloudflare_url}\n")

thread = threading.Thread(target=read_cloudflare_logs)
thread.start()

while cloudflare_url is None:
    time.sleep(1)

os.environ["WEBHOOK_URL"] = cloudflare_url
os.environ["N8N_PROTOCOL"] = "https"
os.environ["N8N_HOST"] = cloudflare_url.replace("https://", "")

print("🚀 Starting n8n...\n")

n8n_process = subprocess.Popen(
    ["n8n", "start"],
    env=os.environ
)

print("\n🎉 Everything running successfully!\n")
print(f"🌍 Public URL: {cloudflare_url}")
print("💻 n8n: http://localhost:5678")

n8n_process.wait()
```

---

# ▶️ Run Everything

Open PowerShell:

```bash
python start_n8n.py
```

Script automatically:

✅ Starts Cloudflare Tunnel
✅ Creates HTTPS URL
✅ Configures webhook variables
✅ Starts n8n
✅ Keeps everything running

No manual work 😌

---

# 🔥 VERY IMPORTANT

After workflow is ready:

# ✅ Click:

```txt
ACTIVE
```

top-right in n8n.

---

# ❌ DO NOT CLICK

```txt
Test Workflow
```

after activating.

Telegram Trigger cannot:

* test
  AND
* production listen

simultaneously.

---

# 🧪 How To Use Bot

Send:

```txt
https://github.com
```

Bot replies:

📦 QR Code Image

Send:

```txt
hello
```

Bot replies:

```txt
❌ Please send valid URL
```

---

# ⚠️ Common Problems

---

## ❌ HTTPS webhook error

Cause:

```txt
localhost / HTTP used
```

Fix:

```txt
Use Cloudflare tunnel
```

---

## ❌ Trigger works only once

Cause:

```txt
Using Test Workflow
```

Fix:

```txt
Activate workflow instead
```

---

## ❌ Telegram webhook conflict

Cause:

```txt
Testing + Active simultaneously
```

Fix:

```txt
Only use ACTIVE mode
```

---

# 🏆 Final Result

You now have:

✅ Telegram QR Generator Bot
✅ Infinite webhook listener
✅ Automatic HTTPS setup
✅ Fully automated startup
✅ No ngrok dependency
✅ Continuous local deployment
✅ Production-like setup for FREE

Which is honestly ridiculous power for a local machine 😌

---

# 💡 Future Upgrades

Possible next improvements:

* 🎨 Custom QR themes
* 🖼 Logo inside QR
* 📊 Analytics dashboard
* 💾 Save QR history
* ☁️ VPS deployment
* 💰 UPI QR generator
* 🤖 Multi-command Telegram bot

---

# 👨‍💻 Author Notes

If something breaks:

* restart Python script
* ensure workflow is ACTIVE
* ensure internet exists
* blame Telegram first

Works surprisingly well after that 😌
