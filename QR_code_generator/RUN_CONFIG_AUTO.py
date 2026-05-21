import subprocess
import threading
import re
import os
import time

cloudflare_url = None

print("🚀 Starting Cloudflare Tunnel...\n")

# Start cloudflared process
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
            print(f"\n✅ Cloudflare URL Found: {cloudflare_url}\n")

thread = threading.Thread(target=read_cloudflare_logs)
thread.start()

# Wait until URL appears
while cloudflare_url is None:
    time.sleep(1)

print("⚙️ Setting n8n environment variables...\n")

# Set environment variables
os.environ["WEBHOOK_URL"] = cloudflare_url
os.environ["N8N_PROTOCOL"] = "https"
os.environ["N8N_HOST"] = cloudflare_url.replace("https://", "")

print("🚀 Starting n8n...\n")

# Start n8n
n8n_process = subprocess.Popen(
    ["n8n", "start"],
    env=os.environ
)

print("\n🎉 Everything is running successfully!\n")
print(f"🌍 Public HTTPS URL: {cloudflare_url}")
print("💻 n8n Dashboard: http://localhost:5678")
print("🤖 Telegram webhook should now work correctly.")
print("\n⚠️ Keep this terminal open.\n")

n8n_process.wait()
