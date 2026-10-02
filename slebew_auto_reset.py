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

BASE = "https://hiphub.cloud"

SESSION = "f1745290c607b177028704e6:48b3920ad0da4b5e69fe7bdb5125e3fb3c3beb605ade998115753818df679fb5d7c9a6befc2689e9bb78e860be22ad671a1b6b4ad2abe6d97c34426ae76bb0e8ed72600eefd6fc428112a1d05bb9424eef11b171b6623901e86ab4c1:5276cdca3c9a7b03ff5200459c721499"
KEY = "HIPHUB-PREMIUM-FBF7-EA8B"

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
