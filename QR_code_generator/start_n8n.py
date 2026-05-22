"""
start_n8n.py  —  One file. Double-click. Everything runs.
─────────────────────────────────────────────────────────
Flow:
  1. Kills any leftover cloudflared / n8n processes from last run
  2. Starts cloudflared tunnel via Git Bash → logs to cloudflare.log
  3. Reads log until trycloudflare URL appears
  4. Writes a run_n8n.bat with env vars baked in → runs it via cmd.exe
  5. Waits for n8n to boot (polls localhost:5678)
  6. Auto-refreshes Telegram webhook (deactivate → activate every workflow)
  7. Keeps running forever — Ctrl+C to stop

Requirements:
  - Git for Windows  : C:\Program Files\Git\git-bash.exe
  - cloudflared.exe  : C:\cloudflared\cloudflared-windows-amd64.exe
                       (or any location — auto-detected)
  - n8n              : installed via  npm install -g n8n
  - Python 3         : with 'requests' library (pip install requests)
"""

import subprocess
import sys
import os
import re
import time
import shutil
import threading

# ── Install requests if missing ───────────────────────────────
try:
    import requests
except ImportError:
    print("Installing 'requests' library...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION  — edit these if your paths differ
# ═══════════════════════════════════════════════════════════════

# Where this script lives (project folder)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Log file written by cloudflared
LOG_FILE = os.path.join(SCRIPT_DIR, "cloudflare.log")

# URL cache file
URL_FILE = os.path.join(SCRIPT_DIR, "url.txt")

# Temp folder (always space-free — avoids Windows path-space bugs)
TEMP_DIR = r"C:\n8n_launcher"

# n8n local address
N8N_LOCAL = "http://localhost:5678"

# How long to wait for cloudflared URL (seconds)
CF_TIMEOUT = 90

# How long to wait for n8n to boot (seconds)
N8N_BOOT_TIMEOUT = 60

# ═══════════════════════════════════════════════════════════════

def banner(msg):
    print(f"\n{'='*54}\n  {msg}\n{'='*54}")

def step(msg):
    print(f"\n>>> {msg}")

def ok(msg):
    print(f"    OK: {msg}")

def err(msg):
    print(f"    ERROR: {msg}")

# ── Find Git Bash ─────────────────────────────────────────────
def find_git_bash():
    candidates = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        r"C:\Git\bin\bash.exe",
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    found = shutil.which("bash")
    if found:
        return found
    return None

# ── Find cloudflared ──────────────────────────────────────────
def find_cloudflared():
    candidates = [
        r"C:\cloudflared\cloudflared-windows-amd64.exe",
        r"C:\cloudflared\cloudflared.exe",
        r"C:\Windows\System32\cloudflared.exe",
        r"C:\Windows\cloudflared.exe",
        r"C:\Program Files\cloudflared\cloudflared.exe",
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    found = shutil.which("cloudflared")
    if found:
        return found
    return None

# ── Find n8n.cmd (npm global install on Windows) ─────────────
def find_n8n():
    # Ask npm where its global prefix is
    try:
        result = subprocess.run(
            ["npm", "config", "get", "prefix"],
            capture_output=True, text=True, timeout=10
        )
        prefix = result.stdout.strip()
        if prefix:
            candidate = os.path.join(prefix, "n8n.cmd")
            if os.path.isfile(candidate):
                return candidate
            candidate = os.path.join(prefix, "n8n")
            if os.path.isfile(candidate):
                return candidate
    except Exception:
        pass

    # Fallback: common locations
    username = os.environ.get("USERNAME", os.environ.get("USER", ""))
    fallbacks = [
        rf"C:\Users\{username}\AppData\Roaming\npm\n8n.cmd",
        r"C:\Program Files\nodejs\n8n.cmd",
    ]
    for p in fallbacks:
        if os.path.isfile(p):
            return p

    found = shutil.which("n8n")
    if found:
        return found
    return None

# ── Kill leftover processes ───────────────────────────────────
def kill_leftovers():
    step("Cleaning up any previous cloudflared / n8n processes...")
    for name in ["cloudflared", "node"]:
        subprocess.run(
            ["taskkill", "/F", "/IM", f"{name}.exe"],
            capture_output=True
        )
    time.sleep(1)
    ok("Clean.")

# ── Start cloudflared, log to file ───────────────────────────
def start_cloudflared(bash_exe, cloudflared_exe):
    step("Starting Cloudflare Tunnel...")

    # Delete stale log
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    # Build bash command — cloudflared path may have spaces, quote it
    # Use Windows-style path for the exe but bash handles it fine
    bash_log = LOG_FILE.replace("\\", "/")
    cf_path   = cloudflared_exe.replace("\\", "/")

    bash_cmd = f'"{cf_path}" tunnel --url http://localhost:5678 >> "{bash_log}" 2>&1'

    proc = subprocess.Popen(
        [bash_exe, "--login", "-c", bash_cmd],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    ok(f"cloudflared started (PID {proc.pid})")
    return proc

# ── Poll log for trycloudflare URL ───────────────────────────
def wait_for_url():
    step(f"Waiting for Cloudflare URL (up to {CF_TIMEOUT}s)...")
    waited = 0
    while waited < CF_TIMEOUT:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            match = re.search(
                r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content
            )
            if match:
                url = match.group(0)
                ok(f"URL found: {url}")
                with open(URL_FILE, "w") as f:
                    f.write(url)
                return url
        time.sleep(1)
        waited += 1
        if waited % 10 == 0:
            print(f"    ...{waited}s elapsed")

    # Timeout — show log for debugging
    print("\n    TIMED OUT. Cloudflared log contents:")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            print(f.read())
    else:
        print("    (log file was never created)")
    sys.exit(1)

# ── Write .bat and launch n8n via cmd.exe ────────────────────
def start_n8n(n8n_cmd, cloudflare_url):
    step("Launching n8n...")

    os.makedirs(TEMP_DIR, exist_ok=True)
    bat_path = os.path.join(TEMP_DIR, "run_n8n.bat")
    cf_host  = cloudflare_url.replace("https://", "")

    # Bash expands all variables HERE before writing the file.
    # cmd.exe sees only plain literal values — zero escaping issues.
    bat_content = (
        "@echo off\r\n"
        f"set WEBHOOK_URL={cloudflare_url}\r\n"
        f"set N8N_PROTOCOL=https\r\n"
        f"set N8N_HOST={cf_host}\r\n"
        f"set N8N_EDITOR_BASE_URL={cloudflare_url}\r\n"
        f"set N8N_LOG_LEVEL=info\r\n"
        f'"{n8n_cmd}" start\r\n'
    )

    with open(bat_path, "w", newline="\r\n") as f:
        f.write(bat_content)

    ok(f"Wrote {bat_path}")
    ok(f"  WEBHOOK_URL = {cloudflare_url}")
    ok(f"  N8N_HOST    = {cf_host}")

    # Run the .bat in a NEW console window (independent — survives this script)
    CREATE_NEW_CONSOLE = 0x00000010
    proc = subprocess.Popen(
        ["cmd.exe", "/c", bat_path],
        creationflags=CREATE_NEW_CONSOLE,
        close_fds=True,
    )
    ok(f"n8n started (PID {proc.pid})")
    return proc

# ── Wait until n8n is responding on localhost:5678 ───────────
def wait_for_n8n():
    step(f"Waiting for n8n to boot (up to {N8N_BOOT_TIMEOUT}s)...")
    waited = 0
    while waited < N8N_BOOT_TIMEOUT:
        try:
            r = requests.get(N8N_LOCAL, timeout=2)
            if r.status_code < 500:
                ok("n8n is up!")
                return True
        except Exception:
            pass
        time.sleep(2)
        waited += 2
        if waited % 10 == 0:
            print(f"    ...{waited}s elapsed")
    err("n8n did not respond in time. Check the n8n console window for errors.")
    return False

# ── Auto-refresh Telegram webhook ────────────────────────────
def refresh_webhooks():
    step("Auto-refreshing Telegram webhook registration...")

    api = f"{N8N_LOCAL}/rest/workflows"

    # n8n may need a moment after boot before the API works
    time.sleep(3)

    try:
        r = requests.get(api, timeout=10)
        r.raise_for_status()
    except Exception as e:
        err(f"Could not reach n8n API: {e}")
        print("    The workflow is running but webhook was not auto-refreshed.")
        print("    Manually toggle your workflow OFF then ON in n8n.")
        return

    data = r.json()
    # n8n returns {"data": [...]} in v1+ and plain list in older versions
    workflows = data.get("data", data) if isinstance(data, dict) else data

    if not isinstance(workflows, list):
        err(f"Unexpected API response format: {type(data)}")
        return

    active = [wf for wf in workflows if wf.get("active")]
    print(f"    Found {len(workflows)} workflow(s), {len(active)} active.")

    if not active:
        print("    No active workflows found.")
        print("    Open n8n at http://localhost:5678 and toggle your workflow ACTIVE.")
        return

    for wf in active:
        wf_id = wf["id"]
        name  = wf.get("name", wf_id)
        print(f"    Refreshing: {name}")
        try:
            requests.post(f"{N8N_LOCAL}/rest/workflows/{wf_id}/deactivate", timeout=10)
            time.sleep(1)
            requests.post(f"{N8N_LOCAL}/rest/workflows/{wf_id}/activate",   timeout=10)
            ok(f"Webhook re-registered for '{name}'")
        except Exception as e:
            err(f"Failed for '{name}': {e}")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    banner("n8n + Cloudflare Tunnel — Full Auto Launcher")
    print(f"  Project dir : {SCRIPT_DIR}")
    print(f"  Log file    : {LOG_FILE}")

    # ── Locate tools ─────────────────────────────────────────
    step("Locating tools...")

    bash_exe = find_git_bash()
    if not bash_exe:
        err("Git Bash (bash.exe) not found!")
        err("Install Git for Windows: https://git-scm.com/download/win")
        input("Press Enter to exit...")
        sys.exit(1)
    ok(f"bash.exe       : {bash_exe}")

    cloudflared = find_cloudflared()
    if not cloudflared:
        err("cloudflared not found!")
        err("Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
        err("Place at: C:\\cloudflared\\cloudflared-windows-amd64.exe")
        input("Press Enter to exit...")
        sys.exit(1)
    ok(f"cloudflared    : {cloudflared}")

    n8n_cmd = find_n8n()
    if not n8n_cmd:
        err("n8n not found!")
        err("Run: npm install -g n8n")
        input("Press Enter to exit...")
        sys.exit(1)
    ok(f"n8n            : {n8n_cmd}")

    # ── Kill leftovers ───────────────────────────────────────
    kill_leftovers()

    # ── Start cloudflared ────────────────────────────────────
    cf_proc = start_cloudflared(bash_exe, cloudflared)

    # ── Get URL ──────────────────────────────────────────────
    cloudflare_url = wait_for_url()

    # ── Start n8n ────────────────────────────────────────────
    n8n_proc = start_n8n(n8n_cmd, cloudflare_url)

    # ── Wait for n8n to be ready ─────────────────────────────
    n8n_ready = wait_for_n8n()

    # ── Auto-refresh webhook ─────────────────────────────────
    if n8n_ready:
        refresh_webhooks()

    # ── Final status ─────────────────────────────────────────
    banner("RUNNING!")
    print(f"  Public URL  : {cloudflare_url}")
    print(f"  n8n UI      : {N8N_LOCAL}")
    print()
    print("  NEXT STEP:")
    print("  Open n8n and toggle your workflow to ACTIVE (if not already).")
    print()
    print("  Verify Telegram webhook:")
    print(f"  https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo")
    print()
    print("  Keep this window open. Ctrl+C to stop everything.")
    print("="*54)

    # ── Keep alive — also monitor child processes ─────────────
    try:
        while True:
            # Restart cloudflared if it dies unexpectedly
            if cf_proc.poll() is not None:
                print("\nWARNING: cloudflared exited unexpectedly. Restarting...")
                cf_proc = start_cloudflared(bash_exe, cloudflared)
                new_url = wait_for_url()
                if new_url != cloudflare_url:
                    cloudflare_url = new_url
                    print(f"New URL: {cloudflare_url}")
                    start_n8n(n8n_cmd, cloudflare_url)
                    time.sleep(8)
                    refresh_webhooks()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nStopped by user. Killing processes...")
        cf_proc.terminate()
        subprocess.run(["taskkill", "/F", "/IM", "cloudflared.exe"], capture_output=True)
        subprocess.run(["taskkill", "/F", "/IM", "node.exe"],        capture_output=True)
        print("Done. Goodbye.")


if __name__ == "__main__":
    main()