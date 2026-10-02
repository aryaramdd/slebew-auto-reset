# Slebew Auto Reset (Termux/Python)

Auto-reset HWID key cloud — jalan di Termux, Linux, atau Windows. Langsung jalan, gak perlu config.

## Setup

```
pkg update && pkg install python -y
pip install requests
git clone https://github.com/aryaramdd/slebew-auto-reset
cd slebew-auto-reset
python slebew_auto_reset.py
```

Biar tetap jalan walau layar mati (Termux):

```
termux-wake-lock
python slebew_auto_reset.py
```

Log: `~/slebew_log.txt`

## Cara kerja

- Poll `GET /api/keys/list` tiap 0.5 detik (pakai session cookie)
- Kalau key yang dipantau punya HWID nempel (device baru login), langsung `POST /api/keys/reset-hwid`

Test sekali doang: `python slebew_auto_reset.py --once`
