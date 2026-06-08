"""
start_n8n.py  —  Single Project Launcher for n8n Telegram Bots
==============================================================
Usage:  python start_n8n.py

Starts Cloudflare Tunnel, extracts public HTTPS URL, sets environment
variables (WEBHOOK_URL, N8N_PROTOCOL, N8N_HOST, N8N_PORT), and launches
n8n — all automatically. Kill with Ctrl+C to clean up.
"""

import subprocess, sys, os, re, time, threading

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

PROJECT_NAME = "n8n Telegram Bot"
PORT         = 5678
TEMP_DIR     = r"C:\n8n_launcher"
N8N_LOCAL    = f"http://localhost:{PORT}"
CF_TIMEOUT   = 90

CLOUDFLARED_PATHS = [
    r"C:\cloudflared\cloudflared-windows-amd64.exe",
    r"C:\cloudflared\cloudflared.exe",
    r"C:\Windows\System32\cloudflared.exe",
    r"C:\Windows\cloudflared.exe",
    r"C:\Program Files\cloudflared\cloudflared.exe",
]

def sep(t=""):
    print(f"\n{'='*58}\n  {t}\n{'='*58}" if t else "="*58)

def ok(m):   print(f"  [OK]  {m}")
def info(m): print(f"  [>>]  {m}")
def warn(m): print(f"  [!!]  {m}")

def die(m):
    print(f"\n[FAIL] {m}")
    input("\nPress Enter to exit...")
    sys.exit(1)

def find_cloudflared():
    for p in CLOUDFLARED_PATHS:
        if os.path.isfile(p): return p
    return shutil.which("cloudflared")

def find_n8n():
    try:
        r = subprocess.run(["npm", "config", "get", "prefix"],
            capture_output=True, text=True, timeout=15, creationflags=0x08000000)
        prefix = r.stdout.strip()
        if prefix:
            for name in ["n8n.cmd", "n8n"]:
                c = os.path.join(prefix, name)
                if os.path.isfile(c): return c
    except Exception: pass
    username = os.environ.get("USERNAME", "")
    for p in [rf"C:\Users\{username}\AppData\Roaming\npm\n8n.cmd",
              r"C:\Program Files\nodejs\n8n.cmd"]:
        if os.path.isfile(p): return p
    return shutil.which("n8n")

import shutil

def kill_leftovers():
    sep("Cleanup")
    for exe in ["cloudflared.exe", "cloudflared-windows-amd64.exe"]:
        subprocess.run(["taskkill", "/F", "/IM", exe], capture_output=True)
    try:
        r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if f":{PORT} " in line and "LISTENING" in line:
                pid = line.split()[-1]
                subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                print(f"  Killed PID {pid} (was on port {PORT})")
    except Exception: pass
    time.sleep(1)
    ok("Cleanup done.")

_cf_url  = None
_cf_proc = None

def _read_cf(proc, log_path):
    global _cf_url
    pat = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    with open(log_path, "w", encoding="utf-8") as f:
        for line in proc.stderr:
            f.write(line); f.flush()
            if _cf_url is None:
                m = pat.search(line)
                if m: _cf_url = m.group(0)

def start_tunnel(cf_exe):
    global _cf_proc, _cf_url
    _cf_url = None
    os.makedirs(TEMP_DIR, exist_ok=True)
    log = os.path.join(TEMP_DIR, "cf.log")
    if os.path.exists(log): os.remove(log)

    _cf_proc = subprocess.Popen(
        [cf_exe, "tunnel", "--url", f"http://localhost:{PORT}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1, encoding="utf-8", errors="replace",
    )
    ok(f"Cloudflared PID: {_cf_proc.pid}")
    threading.Thread(target=_read_cf, args=(_cf_proc, log), daemon=True).start()
    return _cf_proc

def wait_for_url(cf_proc):
    info(f"Waiting for Cloudflare URL (up to {CF_TIMEOUT}s)...")
    log = os.path.join(TEMP_DIR, "cf.log")
    for i in range(CF_TIMEOUT):
        if _cf_url:
            ok(f"Public URL: {_cf_url}")
            return _cf_url
        if cf_proc.poll() is not None:
            content = open(log).read() if os.path.exists(log) else "(no log)"
            die(f"cloudflared crashed.\n{content}")
        time.sleep(1)
        if (i+1) % 15 == 0: print(f"  ...{i+1}s elapsed")
    content = open(log).read() if os.path.exists(log) else "(no log)"
    die(f"No URL after {CF_TIMEOUT}s.\n{content}")

def launch_n8n(n8n_cmd, cf_url):
    cf_host = cf_url.replace("https://", "")
    bat = os.path.join(TEMP_DIR, "run_n8n.bat")

    lines = [
        "@echo off",
        f"title n8n  |  {PROJECT_NAME}  |  Port {PORT}",
        "",
        f"set WEBHOOK_URL={cf_url}",
        "set N8N_PROTOCOL=https",
        f"set N8N_HOST={cf_host}",
        f"set N8N_EDITOR_BASE_URL={cf_url}",
        f"set N8N_PORT={PORT}",
        "set N8N_LOG_LEVEL=info",
        "",
        "echo Starting n8n...",
        f'"{n8n_cmd}" start --port {PORT}',
        "pause"
    ]

    with open(bat, "w", newline="\r\n", encoding="utf-8") as f:
        f.write("\r\n".join(lines) + "\r\n")

    ok(f"Batch file: {bat}")
    proc = subprocess.Popen(
        f'cmd.exe /c "{bat}"',
        creationflags=0x00000010,
        close_fds=True,
        shell=True
    )
    ok(f"n8n started (PID {proc.pid})")
    return proc

def wait_for_n8n():
    info(f"Waiting for n8n on port {PORT}...")
    for i in range(0, 120, 2):
        try:
            r = requests.get(N8N_LOCAL, timeout=3)
            if r.status_code < 500:
                ok("n8n is up!")
                return True
        except Exception: pass
        time.sleep(2)
        if (i+2) % 20 == 0: print(f"  ...{i+2}s elapsed")
    warn("n8n didn't respond — check the n8n window.")
    return False

def main():
    sep(f"n8n Single Project Launcher — Port {PORT}")

    cf_exe  = find_cloudflared() or die("cloudflared not found. Install from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
    n8n_cmd = find_n8n() or die("n8n not found. Install: npm install -g n8n")

    kill_leftovers()

    cf_proc = start_tunnel(cf_exe)
    cf_url  = wait_for_url(cf_proc)

    launch_n8n(n8n_cmd, cf_url)
    wait_for_n8n()

    sep("ALL SYSTEMS RUNNING")
    print(f"  Public URL:  {cf_url}")
    print(f"  n8n Editor:  {N8N_LOCAL}")
    print(f"\n  Keep this window open. Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopping...")
        for exe in ["cloudflared.exe", "cloudflared-windows-amd64.exe"]:
            subprocess.run(["taskkill", "/F", "/IM", exe], capture_output=True)
        print("Done.")

if __name__ == "__main__":
    main()
