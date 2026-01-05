# core/app_context.py
import json
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

# --- IMPORT GOOGLE SERVICE ---
try:
    from core.google_service import GoogleService
    HAS_GOOGLE_SERVICE = True
except ImportError:
    HAS_GOOGLE_SERVICE = False
    print("⚠️ Không tìm thấy GoogleService. Một số tính năng Google sẽ bị vô hiệu hóa.")

class AppContext(QObject):
    """
    Singleton Class quản lý trạng thái toàn cục của ứng dụng (Global State).
    Chịu trách nhiệm: Theme, User Session, Global Settings, Google Calendar Integration.
    """
    _instance = None

    # --- EXISTING SIGNALS ---
    theme_changed = pyqtSignal(str)
    user_state_changed = pyqtSignal(object)
    setting_changed = pyqtSignal(str, object)
    navigation_requested = pyqtSignal(int)

    # --- NEW SIGNALS FOR GOOGLE CALENDAR ---
    google_login_state_changed = pyqtSignal(bool, str)  # (success, message)
    google_events_synced = pyqtSignal(str, list)        # (date_str, events)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        if AppContext._instance is not None:
            raise Exception("AppContext là Singleton! Hãy dùng AppContext.instance().")

        # --- DEFAULT STATE ---
        self._current_theme = "spring"
        self._user_data = None
        self._settings = {
            "volume": 80,
            "show_notifications": True,
            "language": "vi",
            "auto_backup": False
        }

        # --- GOOGLE INTEGRATION ---
        self._google_service = None
        self._google_events_cache = {}  # cache: { "YYYY-MM-DD": [event1, event2, ...] }

        print("✅ AppContext (Core) đã khởi động.")

    # =========================================
    # 1. QUẢN LÝ THEME
    # =========================================
    @property
    def current_theme(self):
        return self._current_theme

    def set_theme(self, theme_key: str):
        if self._current_theme != theme_key:
            self._current_theme = theme_key
            self.theme_changed.emit(theme_key)
            print(f"🎨 AppContext: Đã đổi theme sang '{theme_key}'")

    # =========================================
    # 2. QUẢN LÝ USER (ĐĂNG NHẬP/XUẤT)
    # =========================================
    @property
    def user_data(self):
        return self._user_data

    def login(self, user_info: dict):
        self._user_data = user_info
        self.user_state_changed.emit(user_info)
        print(f"👤 AppContext: User '{user_info.get('name')}' đã đăng nhập.")

    def logout(self):
        self._user_data = None
        self.user_state_changed.emit(None)
        print("👋 AppContext: User đã đăng xuất.")

    # =========================================
    # 3. QUẢN LÝ CÀI ĐẶT
    # =========================================
    def get_setting(self, key, default=None):
        return self._settings.get(key, default)

    def set_setting(self, key, value):
        if self._settings.get(key) != value:
            self._settings[key] = value
            self.setting_changed.emit(key, value)
            print(f"⚙️ AppContext: Setting '{key}' đổi thành {value}")

    # =========================================
    # 4. ĐIỀU HƯỚNG
    # =========================================
    def navigate_to(self, page_index: int):
        self.navigation_requested.emit(page_index)

    # =========================================
    # 5. GOOGLE CALENDAR INTEGRATION (MỚI)
    # =========================================
    def _ensure_google_service(self):
        """Khởi tạo GoogleService nếu chưa có."""
        if not HAS_GOOGLE_SERVICE:
            return None
        if self._google_service is None:
            self._google_service = GoogleService()
        return self._google_service

    def google_login(self):
        svc = self._ensure_google_service()
        if svc is None:
            self.google_login_state_changed.emit(False, "Google Calendar service không khả dụng.")
            return

        ok, msg = svc.authenticate()
        if ok:
            # 🔥 LẤY NAME/EMAIL TỪ GOOGLE SERVICE (đã được lưu trong authenticate)
            name = svc._user_name or "Người dùng Google"
            email = svc._user_email or "unknown@example.com"
            self.login({"name": name, "email": email, "source": "google"})
        else:
            self.logout()

        self.google_login_state_changed.emit(ok, msg)

    def google_logout(self):
        """Xóa token và reset toàn bộ trạng thái Google."""
        from core._const import FILE_TOKEN
        if Path(FILE_TOKEN).exists():
            Path(FILE_TOKEN).unlink()
        self._google_service = None
        self._google_events_cache.clear()
        self.logout()
        self.google_login_state_changed.emit(False, "Đã đăng xuất khỏi Google Calendar.")

    def is_google_logged_in(self) -> bool:
        """Kiểm tra xem đã đăng nhập Google hợp lệ chưa."""
        if not self._google_service:
            return False
        return self._google_service.is_authenticated()

    def fetch_google_events(self, date_str: str):
        """Lấy sự kiện Google cho một ngày cụ thể (YYYY-MM-DD)."""
        if not self.is_google_logged_in():
            return []
        events = self._google_service.fetch_events(date_str)
        self._google_events_cache[date_str] = events
        self.google_events_synced.emit(date_str, events)
        return events

    def create_google_event(self, summary: str, start_dt, end_dt, description: str = "",
                            popup_min=None, email_min=None):
        """Tạo sự kiện mới trên Google Calendar."""
        if not self.is_google_logged_in():
            return False, "Chưa đăng nhập Google Calendar."
        return self._google_service.create_event(summary, start_dt, end_dt, description, popup_min, email_min)

    def delete_google_event(self, event_id: str) -> bool:
        """Xóa sự kiện Google theo ID."""
        if not self.is_google_logged_in():
            return False
        return self._google_service.remove_event(event_id)

    def get_cached_google_events(self, date_str: str):
        """Lấy sự kiện đã cache (nếu có), tránh gọi API nhiều lần."""
        return self._google_events_cache.get(date_str, [])