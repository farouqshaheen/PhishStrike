#!/usr/bin/env python3
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
if not os.path.isdir(os.path.join(BASE_DIR, "auth")):
    print("Creating Auth Directory..")
    os.makedirs(os.path.join(BASE_DIR, "auth"))

CONTAINER = "zphisher"
IMAGE = "htrtech/zphisher:latest"
IMG_MIRROR = "ghcr.io/htr-tech/zphisher:latest"
MOUNT_LOCATION = os.path.join(BASE_DIR, "auth")

try:
    check_container_result = subprocess.run(
        ["docker", "ps", "--all", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        check=True,
    )
    check_container = check_container_result.stdout.strip().split("\n")

    if CONTAINER not in check_container:
        print("Creating new container...")
        subprocess.run(
            [
                "docker",
                "create",
                "--interactive",
                "--tty",
                "--volume",
                f"{MOUNT_LOCATION}:/zphisher/auth/",
                "--network",
                "host",
                "--name",
                CONTAINER,
                IMAGE,
            ],
            check=True,
        )

    subprocess.run(["docker", "start", "--interactive", CONTAINER])
except FileNotFoundError:
    print("Docker command not found. Please install Docker.")
except Exception as e:
    print(f"Docker command failed: {e}")
