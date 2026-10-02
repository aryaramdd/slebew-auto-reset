#!/usr/bin/env python3
# Slebew Auto Reset - Termux/Python port
# Auto-reset HWID key cloud, jalan di Termux / Linux / Windows

import json
import os
import sys
import time
from datetime import datetime

try:
    import requests
except ImportError:
    print("[!] requests belum keinstall. Jalankan: pip install requests")
    sys.exit(1)

INTERVAL = 0.5
LOG_FILE = os.path.expanduser("~/slebew_log.txt")
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slebew_config.json")
EXAMPLE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slebew_config.example.json")

BASE = "https://hiphub.cloud"


def load_config():
    session = os.environ.get("SLEBEW_SESSION", "")
    key = os.environ.get("SLEBEW_KEY", "")
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                cfg = json.load(f)
            session = cfg.get("session", session)
            key = cfg.get("key", key)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[!] Config gagal dibaca: {e}")
    if not session:
        print("[!] Session belum diisi!")
        print("    1. Copy %s jadi %s" % (EXAMPLE_FILE, CONFIG_FILE))
        print("    2. Isi 'session' dengan cookie session dari hiphub.cloud")
        print("    Atau: export SLEBEW_SESSION='isi_session_lo'")
        sys.exit(1)
    return session, key or "HIPHUB-PREMIUM-FBF7-EA8B"


SESSION, KEY = load_config()

HEADERS = {
    "Cookie": f"session={SESSION}",
    "Referer": f"{BASE}/dashboard",
    "User-Agent": "Mozilla/5.0",
}

ONCE = "--once" in sys.argv


def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def get_hwids():
    """Return (count, hwids_list) atau (None, None) kalau request gagal."""
    try:
        r = requests.get(
            f"{BASE}/api/keys/list",
            headers=HEADERS,
            timeout=10,
        )
    except requests.RequestException as e:
        log(f"[!] curl gagal: {e}")
        return None, None

    if r.status_code != 200 or not r.text:
        log(f"[!] curl gagal: status={r.status_code} body={r.text[:200]}")
        return None, None

    try:
        res = r.json()
    except json.JSONDecodeError:
        log(f"[!] JSON parse gagal: {r.text[:200]}")
        return None, None

    keys = res.get("keys") or []
    target = next((k for k in keys if k.get("key") == KEY), None)
    if target is None:
        return 0, []

    hwids = target.get("hwids")
    if hwids is None:
        return 0, []
    if isinstance(hwids, str):
        return (1 if hwids else 0), ([hwids] if hwids else [])
    if isinstance(hwids, list):
        return len(hwids), hwids
    return 0, []


def do_reset():
    try:
        r = requests.post(
            f"{BASE}/api/keys/reset-hwid",
            headers={**HEADERS, "Content-Type": "application/json"},
            json={"key": KEY},
            timeout=10,
        )
        log(f"[?] RESET: {r.text}")
    except requests.RequestException as e:
        log(f"[!] RESET gagal: {e}")


def main():
    log("=== SLEBEW AUTO RESET - TERMUX PORT ===")
    log(f"Key: {KEY} | Interval {INTERVAL}s")
    log("")

    last_empty_log = 0

    while True:
        try:
            count, hwids = get_hwids()
            if count is None:
                time.sleep(1)
                continue
            if count > 0:
                log(f"[DETECTED] hwids={count} -> {','.join(str(h) for h in hwids)} -> RESET NOW!")
                do_reset()
                if ONCE:
                    break
            else:
                now = time.time()
                if now - last_empty_log >= 5:
                    log("[-] hwids kosong (0/5) - Menunggu...")
                    last_empty_log = now
        except Exception as e:
            log(f"[!] Loop error: {e}")
        if ONCE:
            break
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
