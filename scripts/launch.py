#!/usr/bin/env python3
import os
import sys
import platform
import subprocess

if "Android" in platform.system():
    PHISHSTRIKE_ROOT = "/data/data/com.termux/files/usr/opt/phishstrike"
else:
    PHISHSTRIKE_ROOT = "/opt/phishstrike"
    os.environ["PHISHSTRIKE_ROOT"] = PHISHSTRIKE_ROOT


def print_file(path):
    try:
        with open(path, "r") as f:
            print(f.read())
    except FileNotFoundError:
        return False
    return True


if len(sys.argv) > 1:
    arg = sys.argv[1]
    if arg in ["-h", "help"]:
        print("To run PhishStrike type `phishstrike` in your cmd\n")
        print("Help:")
        print(" -h | help : Print this menu & Exit")
        print(" -c | auth : View Saved Credentials")
        print(" -i | ip   : View Saved Victim IP\n")
    elif arg in ["-c", "auth"]:
        if not print_file(os.path.join(PHISHSTRIKE_ROOT, "auth", "usernames.dat")):
            print("No Credentials Found !")
            sys.exit(1)
    elif arg in ["-i", "ip"]:
        if not print_file(os.path.join(PHISHSTRIKE_ROOT, "auth", "ip.txt")):
            print("No Saved IP Found !")
            sys.exit(1)
else:
    try:
        os.chdir(PHISHSTRIKE_ROOT)
        subprocess.run(["python3", "./phishstrike.py"])
    except FileNotFoundError:
        print(
            f"Directory {PHISHSTRIKE_ROOT} not found. PhishStrike may not be installed correctly."
        )
