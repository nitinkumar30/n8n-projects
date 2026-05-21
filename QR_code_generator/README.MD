# 🤖📦 QR Code Generator Bot (n8n + Telegram + API)

Welcome to your **QR Code Generator Bot**, built using **n8n automation**, **Telegram Bot API**, and a free QR generation API.

Or in simpler terms:

> You type a link → bot turns it into a QR code → you feel like a tech wizard 🧙‍♂️✨

---

# 🚀 What this project does

This bot:

- Accepts a URL from Telegram 💬  
- Validates it (no nonsense allowed) 🧼  
- Generates a QR code using API ⚡  
- Sends the QR image back to Telegram 📤  

Yes. That’s it. And yes, it feels more powerful than it should.

---

# 🧠 Tech Stack

- 🧩 n8n (automation engine)
- 🤖 Telegram Bot API
- 🌐 QR Code API → https://api.qrserver.com
- 🌍 ngrok (for local webhook tunneling)
- 💻 Optional: Docker / Node.js setup

---

# 🧾 Workflow Overview

```txt
Telegram User
     ↓
Telegram Trigger (n8n)
     ↓
IF Node (URL validation)
     ↓
HTTP Request (QR API)
     ↓
Telegram Send Photo
````

---

# 🛠️ Step-by-step Setup Guide (a.k.a. “why are there so many steps?”)

---

# 1️⃣ Create Telegram Bot 🤖

Go to Telegram and open:

👉 @BotFather
[https://t.me/BotFather](https://t.me/BotFather)

Then:

```
/newbot
```

Follow instructions:

* Name your bot
* Choose username

You will receive:

```
BOT TOKEN 🔑
```

Save it. Don’t lose it. Don’t paste it on Reddit. Please.

---

# 2️⃣ Install n8n ⚙️

### Option A: Docker (recommended for people who enjoy control)

```bash
docker run -it --rm \
-p 5678:5678 \
-v ~/.n8n:/home/node/.n8n \
docker.n8n.io/n8nio/n8n
```

Open:

```
http://localhost:5678
```

---

### Option B: n8n Cloud (for humans who value time)

[https://n8n.io/cloud/](https://n8n.io/cloud/)

---

# 3️⃣ Install ngrok 🌍 (because Telegram hates localhost)

Telegram requires HTTPS. Because of course it does.

Install:
[https://ngrok.com/](https://ngrok.com/)

Then run:

```bash
ngrok http 5678
```

You’ll get something like:

```
https://random-string.ngrok-free.app
```

Copy it. Cherish it. It is now your lifeline.

---

# 4️⃣ Configure n8n environment variables 🧠

Stop n8n and restart with:

```bash
WEBHOOK_URL=https://your-ngrok-url.ngrok-free.app
N8N_PROTOCOL=https
N8N_HOST=your-ngrok-url.ngrok-free.app
n8n start
```

Yes. Telegram is picky. No, it will not forgive you.

---

# 5️⃣ Build Workflow in n8n 🧩

---

## 🔹 Node 1: Telegram Trigger

* Event: **On Message**
* Credentials: Telegram Bot Token

This listens to user messages like a nosy neighbor.

---

## 🔹 Node 2: IF Node (URL Validation) 🧼

Condition:

```
{{$json["message"]["text"]}} matches regex ^https?:\/\/[^\s]+$
```

### TRUE → valid URL

### FALSE → reject user

Because chaos must be controlled.

---

## 🔹 Node 3: HTTP Request (QR Generator) ⚡

URL:

```txt
https://api.qrserver.com/v1/create-qr-code/?data={{encodeURIComponent($json["message"]["text"])}}&size=350x350&color=1a73e8&bgcolor=ffffff&qzone=4&margin=10&format=png
```

Settings:

* Method: GET
* Response: File
* Binary Property: `data`

---

## 🔹 Node 4: Telegram Send Photo 📤

* Chat ID:

```txt
{{$node["Telegram Trigger"].json["message"]["chat"]["id"]}}
```

* Binary Property: `data`

Caption:

```
Here is your QR code. Try not to break it. 😌
```

---

## ❌ ELSE branch (invalid input)

Send message:

```
❌ Please send a valid URL starting with http:// or https://
```

---

# 🎯 How to Use Bot

Send:

```
https://google.com
```

Bot replies:

📦 QR code image

Send:

```
hello
```

Bot replies:

💀 “Please send a valid URL”

---

# 🧪 Example QR API Output

```txt
https://api.qrserver.com/v1/create-qr-code/?data=https://google.com&size=350x350
```

Boom. QR code appears like magic. (It’s not magic. It’s HTTP.)

---

# ⚠️ Common Issues (a.k.a. pain points)

### ❌ Telegram webhook error

👉 You forgot HTTPS (use ngrok)

---

### ❌ Bot not responding

👉 Wrong token or trigger not active

---

### ❌ QR not generated

👉 URL not encoded properly

---

# 🚀 Possible Upgrades

If you’re feeling dangerous:

* 🎨 Custom QR colors per user
* 🖼 Logo inside QR code
* 📊 Analytics tracking clicks
* 💰 UPI payment QR generator
* 📂 Save QR history to Google Sheets
* 🤖 Multi-language bot support

---

# 💡 Final Thoughts

You didn’t just build a QR bot.

You built:

> A tiny automation system that turns boring links into scannable pixels of joy.

Which is honestly… suspiciously powerful for something built in n8n.

---

# 🧑‍💻 Author Notes

If something breaks:

* It’s probably Telegram
* Or ngrok
* Or you
* Or all three

## Author

[Nitin Kumar](https://www.linkedin.com/in/nitin30kumar/)


Good luck 🍀