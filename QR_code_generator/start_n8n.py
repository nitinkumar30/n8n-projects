"""
start_single_project.py  —  Single Isolated Project Launcher
===========================================================
"""
import subprocess, sys, os, re, time, shutil, threading

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

TARGET_PROJECT = "IPStack Telegram Intelligent Bot"
PORT           = 5678
TEMP_DIR       = r"C:\n8n_launcher"
N8N_LOCAL      = f"http://localhost:{PORT}"

def sep(t=""):  print(f"\n{'='*58}\n  {t}\n{'='*58}" if t else "="*58)
def ok(m):      print(f"  [OK]  {m}")
def die(m):     print(f"[FAIL] {m}"); sys.exit(1)

def find_cloudflared():
    for p in [r"C:\cloudflared\cloudflared-windows-amd64.exe", r"C:\cloudflared\cloudflared.exe"]:
        if os.path.isfile(p): return p
    return shutil.which("cloudflared")

def find_n8n():
    username = os.environ.get("USERNAME", "")
    p = rf"C:\Users\{username}\AppData\Roaming\npm\n8n.cmd"
    if os.path.isfile(p): return p
    return shutil.which("n8n")

def main():
    sep("Single Project Safe Boot Setup")
    cf_exe = find_cloudflared() or die("Cloudflared executable missing.")
    n8n_cmd = find_n8n() or die("n8n terminal engine missing.")
    
    # Clean up old lingering runtime tasks
    for exe in ["cloudflared.exe", "cloudflared-windows-amd64.exe"]:
        subprocess.run(["taskkill", "/F", "/IM", exe], capture_output=True)
        
    # Launch Tunneling
    os.makedirs(TEMP_DIR, exist_ok=True)
    proc = subprocess.Popen([cf_exe, "tunnel", "--url", f"http://localhost:{PORT}"], stderr=subprocess.PIPE, text=True)
    
    cf_url = None
    for _ in range(30):
        line = proc.stderr.readline()
        m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if m:
            cf_url = m.group(0)
            break
        time.sleep(0.5)
        
    if not cf_url: die("Failed to secure safe dynamic tunnel string.")
    ok(f"Tunnel Domain Secured -> {cf_url}")

    # Build execution scripts
    bat = os.path.join(TEMP_DIR, "run_n8n_single.bat")
    with open(bat, "w", newline="\r\n", encoding="utf-8") as f:
        f.write(f"@echo off\r\nset WEBHOOK_URL={cf_url}\r\nset N8N_PORT={PORT}\r\n\"{n8n_cmd}\" start\r\n")
        
    # Execute safely using absolute safe strings
    subprocess.Popen(f'cmd.exe /c "{bat}"', creationflags=0x00000010, shell=True)
    ok("System successfully injected. Keep launcher terminal runtime instance active.")
    
    try:
        while True: time.sleep(5)
    except KeyboardInterrupt: pass

if __name__ == "__main__":
    main()