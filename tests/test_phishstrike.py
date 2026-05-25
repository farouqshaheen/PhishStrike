import sys, os

sys.path.insert(0, ".")

# Test 1: All imports
print("[TEST 1] Checking imports...")
import qrcode
from phishstrike.core import database
from phishstrike.lib import ai_assistant
from phishstrike import state
from phishstrike.runner import main
from phishstrike.capture.monitor import capture_data
from phishstrike.cli.menu import main_menu

print("  PASS: All core imports OK")
print("  PASS: phishstrike package imports OK")

# Test 2: Dashboard deps
print("[TEST 2] Checking dashboard dependencies...")
from flask import Flask
from flask_socketio import SocketIO
import pandas
import openpyxl
from fpdf import FPDF
import requests

print("  PASS: All dashboard deps OK")

# Test 3: database init
print("[TEST 3] Testing database init...")
database.init_db()
print("  PASS: database.init_db() OK")

# Test 4: QR code generation
print("[TEST 4] Testing QR code generation...")
import tempfile

qr = qrcode.QRCode(version=1, box_size=5, border=2)
qr.add_data("https://example.com")
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
tmp = tempfile.mktemp(suffix=".png")
img.save(tmp)
os.remove(tmp)
print("  PASS: QR code generation OK")

# Test 5: requirements.txt completeness
print("[TEST 5] Checking requirements.txt packages...")
required = [
    "qrcode",
    "flask",
    "flask-socketio",
    "google-generativeai",
    "pandas",
    "openpyxl",
    "fpdf2",
    "requests",
    "pillow",
    "cryptography",
]
with open("requirements.txt", "r") as f:
    req_content = f.read().lower()
for pkg in required:
    assert pkg.lower() in req_content, f"Missing from requirements.txt: {pkg}"
print("  PASS: requirements.txt contains all packages")

print()
print("=" * 55)
print("ALL TESTS PASSED - PhishStrike is ready to launch!")
print("=" * 55)
