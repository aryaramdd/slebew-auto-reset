# Slebew Auto Reset (Termux/Python)

Auto-reset HWID key cloud — versi Python yang jalan di Termux, Linux, atau Windows.

## Cara kerja

- Poll `GET /api/keys/list` tiap 0.5 detik (pakai session cookie)
- Kalau key yang dipantau punya HWID nempel (device baru login), langsung `POST /api/keys/reset-hwid`

## Setup

1. Install Python + requests:

```
pkg update && pkg install python -y
pip install requests
```

2. Bikin config (jangan commit file ini):

```
cp slebew_config.example.json slebew_config.json
```

Edit `slebew_config.json`, isi `session` dengan cookie session dari browser saat login di situsnya.

Alternatif pakai env variable:

```
export SLEBEW_SESSION='isi_session_lo'
export SLEBEW_KEY='KEY_LO'   # opsional
```

## Jalankan

```
python slebew_auto_reset.py
```

Test sekali doang (cek status, sekali reset kalau ada hwid):

```
python slebew_auto_reset.py --once
```

Biar tetap jalan walau layar mati (Termux):

```
termux-wake-lock
python slebew_auto_reset.py
```

Log: `~/slebew_log.txt`

## Catatan

- Session cookie itu credential. Kalau bocor, orang lain bisa akses akun lo. Jangan pernah commit `slebew_config.json`.
- Session expired? Logout/login lagi di browser, copy cookie baru.
