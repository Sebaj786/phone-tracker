# ─────────────────────────────────────────────────
#  android/service.py  —  Background Location Service
#
#  Ye file ek alag Android Service ke roop mein
#  chalti hai — app close hone ke baad bhi.
#  Har INTERVAL seconds mein GPS location leke
#  Flask backend ko POST karta hai.
# ─────────────────────────────────────────────────

import time
import json
import urllib.request
import urllib.error
from datetime import datetime

# ── Config (main.py se match karna chahiye) ──────
BACKEND_URL = "http://10.52.217.60:5000"    # ← laptop ka LAN IP
API_KEY     = "mera-super-secret-key-123"   # ← apna key
INTERVAL    = 300                            # 5 minute (seconds mein)
DEVICE_NAME = "My Android"                  # ← apna naam rakho


# ─────────────────────────────────────────────────
#  📍 GPS Location — Android API (jnius se)
# ─────────────────────────────────────────────────
def get_location():
    """
    Android ke LocationManager se last known location lo.
    Pehle GPS try karta hai, nahi mila to Network use karta hai.
    """
    try:
        from jnius import autoclass

        PythonService   = autoclass('org.kivy.android.PythonService')
        Context         = autoclass('android.content.Context')
        LocationManager = autoclass('android.location.LocationManager')

        ctx = PythonService.mService

        lm = ctx.getSystemService(Context.LOCATION_SERVICE)

        # GPS Provider (exact location)
        loc = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER)

        # Network fallback (agar GPS na mile)
        if loc is None:
            loc = lm.getLastKnownLocation(LocationManager.NETWORK_PROVIDER)

        if loc is not None:
            return {
                "latitude":  loc.getLatitude(),
                "longitude": loc.getLongitude(),
                "accuracy":  loc.getAccuracy(),   # meters mein
            }

    except Exception as e:
        log(f"Location error: {e}")

    return None


# ─────────────────────────────────────────────────
#  🔋 Battery Level
# ─────────────────────────────────────────────────
def get_battery():
    """Android BatteryManager se battery % lo"""
    try:
        from jnius import autoclass

        PythonService  = autoclass('org.kivy.android.PythonService')
        Context        = autoclass('android.content.Context')
        BatteryManager = autoclass('android.os.BatteryManager')

        ctx = PythonService.mService
        bm  = ctx.getSystemService(Context.BATTERY_SERVICE)

        level = bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        return level if level >= 0 else None

    except Exception as e:
        log(f"Battery error: {e}")
        return None


# ─────────────────────────────────────────────────
#  📡 Backend ko Location Bhejo
# ─────────────────────────────────────────────────
def send_location(lat, lng, accuracy=None, battery=None):
    """Flask backend ke /api/location pe POST karo"""

    payload = json.dumps({
        "latitude":    lat,
        "longitude":   lng,
        "accuracy":    accuracy,
        "battery":     battery,
        "device_name": DEVICE_NAME,
    }).encode("utf-8")

    req = urllib.request.Request(
        url=f"{BACKEND_URL}/api/location",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key":    API_KEY,
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=15) as response:
        result = json.loads(response.read().decode())
        return result


# ─────────────────────────────────────────────────
#  📝 Simple Logger
# ─────────────────────────────────────────────────
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


# ─────────────────────────────────────────────────
#  🔄 Main Loop
# ─────────────────────────────────────────────────
def main():
    log("📡 PhoneTrack Service started")
    log(f"⏱  Interval: {INTERVAL}s | Server: {BACKEND_URL}")

    fail_count = 0

    while True:
        try:
            # Location lo
            loc     = get_location()
            battery = get_battery()

            if loc is None:
                log("⚠️  Location nahi mili — GPS on hai? Permission hai?")
                fail_count += 1
            else:
                # Backend ko bhejo
                result = send_location(
                    lat=loc["latitude"],
                    lng=loc["longitude"],
                    accuracy=loc.get("accuracy"),
                    battery=battery
                )
                bat_str = f"{battery}%" if battery is not None else "?"
                log(
                    f"✅ Sent | "
                    f"{loc['latitude']:.5f}, {loc['longitude']:.5f} | "
                    f"🔋{bat_str} | "
                    f"ID:{result.get('id', '?')}"
                )
                fail_count = 0  # reset on success

        except urllib.error.URLError as e:
            fail_count += 1
            log(f"❌ Network error ({fail_count}): {e.reason}")

        except Exception as e:
            fail_count += 1
            log(f"❌ Error ({fail_count}): {e}")

        # Zyada fail ho to thoda aur wait karo
        wait = INTERVAL if fail_count < 5 else INTERVAL * 2
        log(f"💤 Next check in {wait}s…")
        time.sleep(wait)


# ─────────────────────────────────────────────────
if __name__ == "__main__":
    main()