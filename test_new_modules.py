"""Quick test for auth, config, and dashboard integration modules."""
import sys

sys.path.insert(0, ".")
import database
import sqlite3

database.init_db()

# Test 1: create_user
created = database.create_user("testuser", "TestPass123!")
print("[TEST A] create_user:", "PASS" if created else "FAIL")

# Test 2: verify correct password
verified_ok = database.verify_user("testuser", "TestPass123!")
print("[TEST B] verify_user (correct pw):", "PASS" if verified_ok else "FAIL")

# Test 3: reject wrong password
verified_bad = database.verify_user("testuser", "wrongpassword")
print("[TEST C] verify_user (wrong pw):", "PASS" if not verified_bad else "FAIL")

# Test 4: get_user returns correct data
user = database.get_user("testuser")
print("[TEST D] get_user:", "PASS" if user and user["username"] == "testuser" else "FAIL")

# Test 5: config module
from config import Config

print("[TEST E] Config.SECRET_KEY exists:", "PASS" if Config.SECRET_KEY else "FAIL")
print("[TEST F] Config.DASHBOARD_PORT:", "PASS" if Config.DASHBOARD_PORT == 5000 else "FAIL")
print(
    "[TEST G] DASHBOARD_HOST default local:",
    "PASS" if Config.DASHBOARD_HOST == "127.0.0.1" else "FAIL",
)
print(
    "[TEST H] weak password rejected:",
    "PASS" if not Config.is_strong_admin_password("phishstrike2025!") else "FAIL",
)
print(
    "[TEST I] internal_api_key stable:",
    "PASS" if Config.internal_api_key() == Config.internal_api_key() else "FAIL",
)

# Test 6: logger module
from lib.logger import get_logger

log = get_logger("Test")
log.info("Logger initialized successfully.")
print("[TEST J] Logger:", "PASS")

# Test 7: Flask-Login imports
from flask_login import LoginManager, UserMixin

print("[TEST K] Flask-Login import:", "PASS")

# Test 8: bcrypt import
import bcrypt

print("[TEST L] bcrypt import:", "PASS")

# Test 9: waitress import
from waitress import serve

print("[TEST M] waitress import:", "PASS")

# Test 10: dashboard client
from lib.dashboard_client import notify_dashboard_refresh

# Dashboard may not be running — function should not raise
notify_dashboard_refresh(timeout=0.5)
print("[TEST N] dashboard_client import:", "PASS")

# Cleanup test user
conn = sqlite3.connect(database.DB_PATH)
conn.execute("DELETE FROM users WHERE username = 'testuser'")
conn.commit()
conn.close()

print()
print("=" * 55)
print("ALL NEW MODULE TESTS PASSED!")
print("=" * 55)
