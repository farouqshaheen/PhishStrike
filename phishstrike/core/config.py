"""
PhishStrike - Central Configuration Module
Loads environment variables from .env file with secure fallback defaults.
"""

import hashlib
import hmac
import os
import secrets

from dotenv import load_dotenv

load_dotenv()

WEAK_ADMIN_PASSWORDS = frozenset(
    {
        "",
        "admin",
        "password",
        "12345678",
        "phishstrike",
        "phishstrike2025!",
    }
)


class Config:
    # ─── Flask Core ──────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

    # ─── Database ────────────────────────────────────────────────────────
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DB_PATH = os.environ.get(
        "DB_PATH", os.path.join(BASE_DIR, "auth", "phishstrike.db")
    )

    # ─── Dashboard ───────────────────────────────────────────────────────
    DASHBOARD_HOST = os.environ.get("DASHBOARD_HOST", "127.0.0.1")
    DASHBOARD_PORT = int(os.environ.get("DASHBOARD_PORT", 5000))
    # socketio = WebSocket live feed; waitress = HTTP only (UI polls every 5s)
    DASHBOARD_RUNTIME = os.environ.get("DASHBOARD_RUNTIME", "socketio").lower()

    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "http://127.0.0.1:5000,http://localhost:5000",
    )

    # ─── Admin (first-run; set ADMIN_PASSWORD in .env or use scripts/setup_admin.py)
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

    INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY")

    # ─── Capture storage ─────────────────────────────────────────────────
    CAPTURE_ENCRYPT = os.environ.get("CAPTURE_ENCRYPT", "false").lower() == "true"
    RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "0") or "0")

    # ─── Login protection ──────────────────────────────────────────────────
    LOGIN_MAX_ATTEMPTS = int(os.environ.get("LOGIN_MAX_ATTEMPTS", "5"))
    LOGIN_WINDOW_SECONDS = int(os.environ.get("LOGIN_WINDOW_SECONDS", "300"))

    @classmethod
    def internal_api_key(cls) -> str:
        """Shared secret for CLI → dashboard capture notifications."""
        if cls.INTERNAL_API_KEY:
            return cls.INTERNAL_API_KEY
        return hmac.new(
            cls.SECRET_KEY.encode("utf-8"),
            b"phishstrike-dashboard-internal",
            hashlib.sha256,
        ).hexdigest()

    @classmethod
    def is_strong_admin_password(cls, password: str | None) -> bool:
        if not password or len(password) < 8:
            return False
        if password.lower() in WEAK_ADMIN_PASSWORDS:
            return False
        return True

    @classmethod
    def cors_origin_list(cls) -> list[str]:
        return [o.strip() for o in cls.CORS_ORIGINS.split(",") if o.strip()]
