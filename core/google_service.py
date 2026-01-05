# core/google_service.py
"""
Google Calendar Service – kết nối và thao tác với Google Calendar API.
Không chứa UI, không chứa logic nghiệp vụ tài chính.
Chỉ chịu trách nhiệm: authenticate, fetch, create, delete event.
"""

import os
from pathlib import Path
from datetime import datetime
from core._const import FILE_TOKEN, SCOPES, FILE_CRED

# --- GOOGLE API IMPORTS ---
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False


class GoogleService:
    def __init__(self):
        self.service = None
        self.creds = None
        self._user_name = None      # ← THÊM
        self._user_email = None 

# Trong core/google_service.py → hàm authenticate()
    def authenticate(self):
        if not HAS_GOOGLE:
            return False, "Thiếu thư viện Google..."

        try:
            # 1. Tải token nếu có
            if os.path.exists(FILE_TOKEN):
                self.creds = Credentials.from_authorized_user_file(str(FILE_TOKEN), SCOPES)

            # 2. Nếu token hợp lệ → KHÔNG cần flow, chỉ khởi tạo service
            if self.creds and self.creds.valid:
                self.service = build("calendar", "v3", credentials=self.creds)
                # Lấy thông tin user
                oauth2_service = build("oauth2", "v2", credentials=self.creds)
                user_info = oauth2_service.userinfo().get().execute()
                self._user_name = user_info.get("name", "Người dùng Google")
                self._user_email = user_info.get("email", "unknown@example.com")
                return True, f"Đã khôi phục phiên đăng nhập cho {self._user_name}."

            # 3. Nếu token hết hạn nhưng có refresh_token → refresh
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                # Lưu lại token mới
                with open(FILE_TOKEN, "w", encoding="utf-8") as token:
                    token.write(self.creds.to_json())
                self.service = build("calendar", "v3", credentials=self.creds)
                # Lấy user info
                oauth2_service = build("oauth2", "v2", credentials=self.creds)
                user_info = oauth2_service.userinfo().get().execute()
                self._user_name = user_info.get("name", "Người dùng Google")
                self._user_email = user_info.get("email", "unknown@example.com")
                return True, f"Đã gia hạn phiên cho {self._user_name}."

            # 4. Nếu không có token hợp lệ → chạy flow
            if not os.path.exists(FILE_CRED):
                return False, f"Thiếu file credentials: {FILE_CRED}..."

            flow = InstalledAppFlow.from_client_secrets_file(str(FILE_CRED), SCOPES)
            self.creds = flow.run_local_server(port=0)

            # Lưu token
            with open(FILE_TOKEN, "w", encoding="utf-8") as token:
                token.write(self.creds.to_json())

            self.service = build("calendar", "v3", credentials=self.creds)
            oauth2_service = build("oauth2", "v2", credentials=self.creds)
            user_info = oauth2_service.userinfo().get().execute()
            self._user_name = user_info.get("name", "Người dùng Google")
            self._user_email = user_info.get("email", "unknown@example.com")
            return True, f"Đăng nhập thành công! Xin chào, {self._user_name}."

        except Exception as e:
            error_msg = str(e)
            if "invalid_grant" in error_msg:
                if os.path.exists(FILE_TOKEN):
                    os.remove(FILE_TOKEN)
                return False, "Token không hợp lệ. Đã xóa token cũ. Vui lòng đăng nhập lại."
            return False, f"Lỗi xác thực Google: {error_msg}"

    def fetch_events(self, date_str: str):
        """
        Lấy danh sách sự kiện trong ngày `date_str` (YYYY-MM-DD).
        Trả về: list[dict] các sự kiện.
        """
        if not self.service:
            return []

        try:
            start = f"{date_str}T00:00:00Z"
            end = f"{date_str}T23:59:59Z"
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start,
                timeMax=end,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            return events_result.get('items', [])
        except Exception:
            return []

    def create_event(self, summary: str, start_dt: datetime, end_dt: datetime,
                     description: str = "", popup_min=None, email_min=None):
        """
        Tạo sự kiện mới trên Google Calendar.
        Trả về: (success: bool, message: str)
        """
        if not self.service:
            return False, "Chưa kết nối Google Calendar."

        # Chuẩn bị reminder overrides
        overrides = []
        if popup_min is not None:
            overrides.append({'method': 'popup', 'minutes': int(popup_min)})
        if email_min is not None:
            overrides.append({'method': 'email', 'minutes': int(email_min)})

        event_body = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'Asia/Ho_Chi_Minh'
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'Asia/Ho_Chi_Minh'
            },
            'reminders': {
                'useDefault': False,
                'overrides': overrides
            }
        }

        try:
            self.service.events().insert(calendarId='primary', body=event_body).execute()
            return True, "Đã tạo sự kiện trên Google Calendar thành công!"
        except Exception as e:
            return False, f"Lỗi khi tạo sự kiện: {str(e)}"

    def remove_event(self, event_id: str) -> bool:
        """Xóa sự kiện theo ID. Trả về True nếu thành công."""
        if not self.service or not event_id:
            return False
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
        except Exception:
            return False

    def is_authenticated(self) -> bool:
        """Kiểm tra xem đã đăng nhập hợp lệ chưa."""
        return self.service is not None and self.creds is not None and self.creds.valid