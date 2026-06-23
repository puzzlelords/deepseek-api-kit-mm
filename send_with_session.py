import sys
import io
import requests
import json
import os
from pathlib import Path

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"
SESSION_FILE = Path(__file__).parent / ".session_id"

def get_session_id():
    """خواندن session_id از فایل"""
    if SESSION_FILE.exists():
        with open(SESSION_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_session_id(session_id):
    """ذخیره session_id در فایل"""
    with open(SESSION_FILE, 'w') as f:
        f.write(session_id)

def send_message(message, use_existing_session=True):
    """ارسال پیام با مدیریت خودکار session"""
    session_id = None
    if use_existing_session:
        session_id = get_session_id()
    
    payload = {
        "model": "thinking_not_search",
        "messages": [{"role": "user", "content": message}],
        "stream": False
    }
    if session_id:
        payload["session_id"] = session_id
    
    print(f"📤 Sending: {message}")
    print(f"   Session: {session_id or '(new)'}")
    
    resp = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload)
    data = resp.json()
    
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    new_session_id = data.get("session_id")
    
    # ذخیره session_id جدید
    if new_session_id:
        save_session_id(new_session_id)
        print(f"   ✅ Session saved: {new_session_id}")
    
    return content, new_session_id

def reset_session():
    """حذف فایل session_id برای شروع مکالمه‌ی جدید"""
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
        print("🗑️  Session reset successfully.")
    else:
        print("ℹ️  No session to reset.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python send_with_session.py <message>        - Send a message (uses saved session if exists)")
        print("  python send_with_session.py --reset          - Delete saved session")
        sys.exit(1)
    
    if sys.argv[1] == "--reset":
        reset_session()
        sys.exit(0)
    
    message = " ".join(sys.argv[1:])
    content, session_id = send_message(message)
    print(f"\n🤖 Assistant: {content}")