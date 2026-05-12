"""
ذخیره‌سازی پایدار سشن‌ها در فایل JSON
با هر بار ری‌استارت سرور، سشن‌ها از بین نمی‌روند
"""
import json
import os
from typing import Dict, Optional
from common.api import DeepSeekAPI


class SessionStore:
    def __init__(self, file_path: str, api: DeepSeekAPI):
        self.file_path = file_path
        self.api = api
        self._sessions: Dict[str, dict] = {}
        self._load()

    def _load(self):
        """بارگذاری سشن‌ها از فایل JSON"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._sessions = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._sessions = {}

    def _save(self):
        """ذخیره سشن‌ها در فایل JSON"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self._sessions, f, ensure_ascii=False, indent=2)

    def get(self, session_id: str) -> dict:
        """دریافت سشن، اگر وجود نداشت یکی جدید می‌سازد"""
        if session_id not in self._sessions:
            chat_id = self.api.create_chat_session()
            self._sessions[session_id] = {
                "chat_id": chat_id,
                "last_message_id": None,
                "thinking_enabled": True,
                "search_enabled": False,
                "last_message_preview": None,
            }
            self._save()
        return self._sessions[session_id]

    def update(self, session_id: str, data: dict):
        """به‌روزرسانی فیلدهای یک سشن"""
        if session_id in self._sessions:
            self._sessions[session_id].update(data)
            self._save()

    def delete(self, session_id: str) -> bool:
        """حذف یک سشن"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            self._save()
            return True
        return False

    def save(self):
        """ذخیره تغییرات حافظه در فایل JSON"""
        self._save()

    def list_all(self) -> Dict[str, dict]:
        """برگرداندن همه سشن‌ها"""
        return dict(self._sessions)
