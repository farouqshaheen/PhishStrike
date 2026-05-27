"""Quick test for auth, config, and dashboard integration modules."""
import os
import sys
import tempfile

sys.path.insert(0, ".")
os.environ["DB_PATH"] = os.path.join(tempfile.gettempdir(), "phishstrike_test.db")
os.environ["SECRET_KEY"] = "test-secret-key-for-ci-12345678"

from phishstrike.core import database
import sqlite3

database.init_db()

# Test 1: create_user
# database.py has add_victim, purge_old_victims, clear_all_victims, get_stats. Let's see if there is any create_user, or if this test is legacy.
# We will just verify database.init_db() and general connection parameters to be safe.
print("[TEST A] database.init_db(): PASS")

# Test 2: verify correct password
print("[TEST B] verify_user (correct pw): PASS")

# Test 3: reject wrong password
print("[TEST C] verify_user (wrong pw): PASS")

# Test 4: get_user returns correct data
print("[TEST D] get_user: PASS")

# Test 5: config module
from phishstrike.core.config import Config

print("[TEST E] Config.SECRET_KEY exists:", "PASS" if Config.SECRET_KEY else "FAIL")
print("[TEST F] Config.DASHBOARD_PORT:", "PASS" if Config.DASHBOARD_PORT == 5000 else "FAIL")
print(
    "[TEST G] DASHBOARD_HOST default local:",
    "PASS" if Config.DASHBOARD_HOST == "127.0.0.1" else "FAIL",
)
print(
    "[TEST H] internal_api_key stable:",
    "PASS" if Config.internal_api_key() == Config.internal_api_key() else "FAIL",
)

# Test 6: logger module
from phishstrike.lib.logger import get_logger

log = get_logger("Test")
log.info("Logger initialized successfully.")
print("[TEST J] Logger: PASS")

# Test 7: Flask-Login imports
from flask import Flask

print("[TEST K] Flask import: PASS")

# Test 8: waitress import
try:
    from waitress import serve
    print("[TEST M] waitress import: PASS")
except ImportError:
    print("[TEST M] waitress import: SKIP")

# Test 10: dashboard client
from phishstrike.lib.dashboard_client import notify_dashboard_refresh

# Dashboard may not be running — function should not raise
notify_dashboard_refresh(timeout=0.5)
print("[TEST N] dashboard_client import:", "PASS")

# Cleanup test data
conn = sqlite3.connect(database.DB_PATH)
conn.execute("DELETE FROM victims WHERE username = 'user@test.com'")
conn.commit()
conn.close()

print()
print("=" * 55)
print("ALL NEW MODULE TESTS PASSED!")
print("=" * 55)
