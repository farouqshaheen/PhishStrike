import sys, os
sys.path.insert(0, '.')

# Test 1: All imports
print('[TEST 1] Checking imports...')
import qrcode
import database
from lib import ai_assistant
from lib import site_injector
from lib.site_injector import inject_features
print('  PASS: All core imports OK')

# Test 2: Dashboard deps
print('[TEST 2] Checking dashboard dependencies...')
from flask import Flask
from flask_socketio import SocketIO
import pandas
import openpyxl
from fpdf import FPDF
import requests
print('  PASS: All dashboard deps OK')

# Test 3: database init
print('[TEST 3] Testing database init...')
database.init_db()
print('  PASS: database.init_db() OK')

# Test 4: QR code generation
print('[TEST 4] Testing QR code generation...')
import tempfile
qr = qrcode.QRCode(version=1, box_size=5, border=2)
qr.add_data('https://example.com')
qr.make(fit=True)
img = qr.make_image(fill_color='black', back_color='white')
tmp = tempfile.mktemp(suffix='.png')
img.save(tmp)
os.remove(tmp)
print('  PASS: QR code generation OK')

# Test 5: site_injector
print('[TEST 5] Testing site_injector...')
import tempfile, shutil
tmpdir = tempfile.mkdtemp()
login_php_content = "<?php file_put_contents('usernames.txt', 'test'); header('Location: https://google.com'); exit(); ?>"
with open(os.path.join(tmpdir, 'login.php'), 'w') as f:
    f.write(login_php_content)
with open(os.path.join(tmpdir, 'index.html'), 'w') as f:
    f.write('<html><head></head><body></body></html>')
inject_features(tmpdir)
assert os.path.exists(os.path.join(tmpdir, 'log_fingerprint.php')), 'log_fingerprint.php missing'
with open(os.path.join(tmpdir, 'index.html')) as f:
    content = f.read()
assert 'PhishStrike Advanced Fingerprinting' in content, 'fingerprint JS not injected'
shutil.rmtree(tmpdir)
print('  PASS: site_injector inject_features OK')

# Test 6: requirements.txt completeness
print('[TEST 6] Checking requirements.txt packages...')
required = ['qrcode', 'flask', 'flask-socketio', 'google-generativeai', 'pandas', 'openpyxl', 'fpdf2', 'requests', 'pillow']
with open('requirements.txt', 'r') as f:
    req_content = f.read().lower()
for pkg in required:
    assert pkg.lower() in req_content, f'Missing from requirements.txt: {pkg}'
print('  PASS: requirements.txt contains all packages')

print()
print('=' * 55)
print('ALL TESTS PASSED - PhishStrike is ready to launch!')
print('=' * 55)
