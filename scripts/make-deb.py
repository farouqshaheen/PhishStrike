#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import platform

PACKAGE = "phishstrike"
VERSION = "2.3.5"
ARCH = "all"
PKG_NAME = f"{PACKAGE}_{VERSION}_{ARCH}.deb"

if not os.path.exists("scripts/launch.py"):
    print("launch.py should be in the `scripts` Directory. Exiting...")
    sys.exit(1)

depend = "curl, php, unzip"
bin_dir = "usr/bin"
opt_dir = f"opt/{PACKAGE}"

if "termux" in sys.argv or "Android" in platform.system():
    depend = "ncurses-utils, proot, resolv-conf, " + depend
    bin_dir = "data/data/com.termux/files/usr/bin"
    opt_dir = f"data/data/com.termux/files/usr/opt/{PACKAGE}"

if os.path.isdir("build_env"):
    shutil.rmtree("build_env")

os.makedirs(f"build_env/{bin_dir}", exist_ok=True)
os.makedirs(f"build_env/{opt_dir}", exist_ok=True)
os.makedirs("build_env/DEBIAN", exist_ok=True)

with open("build_env/DEBIAN/control", "w") as f:
    f.write(f"""Package: {PACKAGE}
Version: {VERSION}
Architecture: {ARCH}
Maintainer: @htr-tech
Depends: {depend}
Homepage: https://github.com/farouqshaheen/PhishStrike
Description: An automated phishing tool with 30+ templates. This Tool is made for educational purpose only !
""")

with open("build_env/DEBIAN/prerm", "w") as f:
    f.write(f"""#!/usr/bin/env python3
import shutil
shutil.rmtree('/{opt_dir}', ignore_errors=True)
""")

# Note: os.chmod on Windows will not set UNIX executable bits, but this script is meant to be run in UNIX environments anyway.
if platform.system() != "Windows":
    os.chmod("build_env/DEBIAN", 0o755)
    os.chmod("build_env/DEBIAN/control", 0o755)
    os.chmod("build_env/DEBIAN/prerm", 0o755)

shutil.copy2("scripts/launch.py", f"build_env/{bin_dir}/{PACKAGE}")
if platform.system() != "Windows":
    os.chmod(f"build_env/{bin_dir}/{PACKAGE}", 0o755)

# Run from PhishStrike root directory
if not os.path.exists("scripts/launch.py") and os.path.exists("../scripts/launch.py"):
    os.chdir("..")

for item in [
    ".github",
    ".sites",
    "LICENSE",
    "README.md",
    "phishstrike.py",
    "phishstrike",
    "requirements.txt",
    "scripts",
]:
    if os.path.exists(item):
        if os.path.isdir(item):
            shutil.copytree(item, f"build_env/{opt_dir}/{item}")
        else:
            shutil.copy2(item, f"build_env/{opt_dir}")

try:
    subprocess.run(["dpkg-deb", "--build", "./build_env", PKG_NAME])
except FileNotFoundError:
    print(
        "dpkg-deb not found. Ensure you are on a Debian-based system or have it installed."
    )
shutil.rmtree("build_env")
