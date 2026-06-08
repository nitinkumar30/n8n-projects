"""
start_all_projects.py  —  Multi-Project Launcher (SAME PORT 5678)
==================================================================
All projects share ONE n8n instance on port 5678 and ONE Cloudflare
tunnel. A single .bat launches n8n once, with all projects' webhook
URLs pointing to the same tunnel.
"""

import subprocess, sys, os, re, time, shutil, threading

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

# ╔══════════════════════════════════════════════════════════╗
# ║         ★  ADD / REMOVE PROJECTS HERE  ★                ║
# ╚══════════════════════════════════════════════════════════╝
ACTIVE_PROJECTS = [
    "QR Code Generator Bot",
    "IPStack Telegram Intelligent Bot",
    "Naukri Telegram Automation"
]

PORT        = 5678
TEMP_DIR    = r"C:\n8n_launcher"
CF_TIMEOUT  = 90
N8N_TIMEOUT = 120
N8N_LOCAL   = f"http://localhost:{PORT}"

CLOUDFLARED_PATHS = [
    r"C:\cloudflared\cloudflared-windows-amd64.exe",
    r"C:\cloudflared\cloudflared.exe",
    r"C:\Windows\System32\cloudflared.exe",
    r"C:\Windows\cloudflared.exe",
    r"C:\Program Files\cloudflared\cloudflared.exe",
]

def sep(t=""):  print(f"\n{'='*58}\n  {t}\n{'='*58}" if t else "="*58)
def ok(m):      print(f"  [OK]  {m}")
def info(m):    print(f"  [>>]  {m}")
def warn(m):    print(f"  [!!]  {m}")
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
            capture_output=True, text=True, timeout=15,
            creationflags=0x08000000)
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
            ok(f"URL: {_cf_url}")
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
    bat     = os.path.join(TEMP_DIR, "run_n8n_all.bat")

    lines = [
        "@echo off",
        f'title n8n  |  All Projects  |  Port {PORT}',
        "",
        "set WEBHOOK_URL={}".format(cf_url),
        "set N8N_PROTOCOL=https",
        "set N8N_HOST={}".format(cf_host),
        "set N8N_EDITOR_BASE_URL={}".format(cf_url),
        "set N8N_PORT={}".format(PORT),
        "set N8N_LOG_LEVEL=info",
        "",
        "echo Starting n8n...",
        f'"{n8n_cmd}" start --port {PORT}',
        "pause"
    ]

    content = "\r\n".join(lines) + "\r\n"
    with open(bat, "w", newline="\r\n", encoding="utf-8") as f:
        f.write(content)

    ok(f"Bat written: {bat}")
    
    # CRITICAL FIX: Wrapped inside outer quotes to handle space-corrupted paths safely
    proc = subprocess.Popen(
        f'cmd.exe /c "{bat}"',
        creationflags=0x00000010,  # CREATE_NEW_CONSOLE
        close_fds=True,
        shell=True
    )
    ok(f"n8n window opened (PID {proc.pid})")
    return proc

def wait_for_n8n():
    info(f"Waiting for n8n on port {PORT}...")
    for i in range(0, N8N_TIMEOUT, 2):
        try:
            r = requests.get(N8N_LOCAL, timeout=3)
            if r.status_code < 500:
                ok("n8n is up globally!")
                return True
        except Exception: pass
        time.sleep(2)
        if (i+2) % 20 == 0: print(f"  ...{i+2}s elapsed")
    warn("n8n didn't respond — check the n8n window for errors.")
    return False

def refresh_webhooks_for_active_projects():
    info("Refreshing webhooks for active projects...")
    time.sleep(3)
    try:
        r = requests.get(f"{N8N_LOCAL}/rest/workflows", timeout=10)
        r.raise_for_status()
    except Exception as e:
        warn(f"Cannot reach n8n API: {e}")
        return

    data = r.json()
    wfs  = data.get("data", data) if isinstance(data, dict) else data
    if not isinstance(wfs, list): return

    matched = 0
    for wf in wfs:
        wid   = wf["id"]
        wname = wf.get("name", "")
        is_target = any(proj.lower() in wname.lower() or wname.lower() in proj.lower() for proj in ACTIVE_PROJECTS)

        if not is_target: continue
        matched += 1
        try:
            requests.post(f"{N8N_LOCAL}/rest/workflows/{wid}/deactivate", timeout=10)
            time.sleep(0.5)
            requests.post(f"{N8N_LOCAL}/rest/workflows/{wid}/activate", timeout=10)
            ok(f"Webhook registered: {wname}")
        except Exception as e:
            warn(f"Failed for '{wname}': {e}")

    if matched == 0:
        warn("No matching active workflows found in the n8n instance canvas names.")

def main():
    sep("n8n Multi-Project Launcher  —  Single Port Fixed")
    cf_exe  = find_cloudflared() or die("cloudflared not found.")
    n8n_cmd = find_n8n() or die("n8n not found.")
    
    kill_leftovers()
    
    cf_proc = start_tunnel(cf_exe)
    cf_url  = wait_for_url(cf_proc)
    
    n8n_proc = launch_n8n(n8n_cmd, cf_url)
    ready = wait_for_n8n()
    
    if ready:
        refresh_webhooks_for_active_projects()
        
    sep("ALL SYSTEMS RUNNING")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopping...")
        for exe in ["cloudflared.exe", "cloudflared-windows-amd64.exe"]:
            subprocess.run(["taskkill", "/F", "/IM", exe], capture_output=True)

if __name__ == "__main__":
    main()