[app]

# ── App Identity ─────────────────────────────────
title = PhoneTrack
package.name = phonetrack
package.domain = org.sevix

# ── Source ────────────────────────────────────────
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# ── Requirements ──────────────────────────────────
# pyjnius zaroori hai android APIs (Location, Battery) ke liye
requirements = python3,kivy==2.2.1,pyjnius,android

# ── Android Service ───────────────────────────────
# service.py background mein alag process ki tarah chalega
services = PhoneTrackService:service.py

# ── Permissions ───────────────────────────────────
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_BACKGROUND_LOCATION,FOREGROUND_SERVICE,FOREGROUND_SERVICE_LOCATION,WAKE_LOCK,POST_NOTIFICATIONS

# ── Android Build Config ──────────────────────────
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# App orientation
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
