# ─────────────────────────────────────────────────
#  android/main.py  —  PhoneTrack Kivy App (UI)
#  Ye sirf ek simple status screen hai.
#  Asli kaam service.py karta hai background mein.
# ─────────────────────────────────────────────────

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.utils import platform
from kivy.metrics import dp

if platform == "android":
    from android.permissions import request_permissions, Permission, check_permission

# ── Apna Config yahan badlo ──────────────────────
BACKEND_URL = "http://10.52.217.60:5000"    # ← tumhara laptop ka LAN IP
API_KEY     = "mera-super-secret-key-123"   # ← same jo backend mein rakha
INTERVAL    = 300                            # seconds (5 min)


class TrackerApp(App):

    def build(self):
        self.title = "PhoneTrack"

        # Root layout
        root = BoxLayout(
            orientation="vertical",
            padding=dp(24),
            spacing=dp(16)
        )

        # ── Title ──────────────────────────────────
        root.add_widget(Label(
            text="📡 PhoneTrack",
            font_size=dp(26),
            bold=True,
            size_hint_y=None,
            height=dp(50),
            color=(0.0, 0.83, 1.0, 1)   # cyan
        ))

        # ── Status ─────────────────────────────────
        self.lbl_status = Label(
            text="Starting…",
            font_size=dp(15),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=dp(36)
        )
        root.add_widget(self.lbl_status)

        # ── Last Location ───────────────────────────
        self.lbl_location = Label(
            text="Lat: —\nLng: —",
            font_size=dp(13),
            color=(0.9, 0.9, 0.9, 1),
            size_hint_y=None,
            height=dp(60)
        )
        root.add_widget(self.lbl_location)

        # ── Last Sent ───────────────────────────────
        self.lbl_time = Label(
            text="Last sent: —",
            font_size=dp(12),
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(30)
        )
        root.add_widget(self.lbl_time)

        # ── Server URL ──────────────────────────────
        root.add_widget(Label(
            text=f"🖥️  {BACKEND_URL}",
            font_size=dp(11),
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(28)
        ))

        # ── Spacer ──────────────────────────────────
        root.add_widget(Label())

        # ── Info Text ───────────────────────────────
        root.add_widget(Label(
            text="App close kar do — service\nbackground mein chalti rahegi ✅",
            font_size=dp(12),
            color=(0.3, 0.7, 0.3, 1),
            halign="center",
            size_hint_y=None,
            height=dp(60)
        ))

        # Permission maango, phir service start karo
        Clock.schedule_once(self._request_permissions, 1)

        return root

    # ── Runtime Permissions (Android 6+ zaroori) ────
    def _request_permissions(self, *args):
        if platform != "android":
            self.lbl_status.text  = "⚠️ Android pe hi chalega"
            self.lbl_status.color = (1, 0.72, 0, 1)
            return

        needed = [
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
        ]
        # Android 10+ (API 29+) pe background location alag se maangni padti hai
        try:
            needed.append(Permission.ACCESS_BACKGROUND_LOCATION)
        except AttributeError:
            pass  # purane Android version pe ye permission exist nahi karti
        # Android 13+ (API 33+) pe notification permission bhi chahiye
        try:
            needed.append(Permission.POST_NOTIFICATIONS)
        except AttributeError:
            pass

        self.lbl_status.text  = "Permission maang rahe hain…"
        self.lbl_status.color = (1, 0.72, 0, 1)

        request_permissions(needed, self._on_permissions_result)

    def _on_permissions_result(self, permissions, grants):
        if all(grants):
            self._start_service()
        else:
            self.lbl_status.text  = "❌ Permission deny hui — Settings mein 'Allow all the time' set karo"
            self.lbl_status.color = (1, 0.28, 0.34, 1)

    # ── Service Start ───────────────────────────────
    def _start_service(self, *args):
        try:
            from android import AndroidService
            self.service = AndroidService(
                "PhoneTrack",                # Notification title
                "Location tracking active"   # Notification text
            )
            self.service.start("started")
            self.lbl_status.text  = "✅ Service chal rahi hai"
            self.lbl_status.color = (0.13, 0.85, 0.43, 1)
        except Exception as e:
            self.lbl_status.text  = f"❌ Service error: {e}"
            self.lbl_status.color = (1, 0.28, 0.34, 1)

    # ── App Background mein jaaye to bhi chale ──────
    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    TrackerApp().run()