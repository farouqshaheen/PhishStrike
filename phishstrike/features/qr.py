import os

import qrcode

from phishstrike import state
from lib.terminal_ui import *


def generate_qr(url: str) -> None:
    state.qr_counter += 1
    slow_type(
        "    [+] Initializing Tactical QR Engine...",
        speed=0.01,
        start_rgb=RGB_WHITE,
        end_rgb=RGB_PURPLE,
    )
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        qr_dir = os.path.join(state.BASE_DIR, "qrcodes")
        os.makedirs(qr_dir, exist_ok=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_path = os.path.join(qr_dir, f"qr_code_{state.qr_counter}.png")
        img.save(qr_path)
        slow_type(
            f"    [+] Intelligence QR Secured at: qr_code_{state.qr_counter}.png",
            speed=0.01,
            start_rgb=RGB_WHITE,
            end_rgb=RGB_CYAN,
        )
        slow_type(
            "    [!] QR Code for Scanning Ready:",
            speed=0.01,
            start_rgb=RGB_CYAN,
            end_rgb=RGB_WHITE,
        )
        print()
        qr.print_ascii(tty=True)
        print()
    except Exception as e:
        print(f"\n{DARK}[{WHITE}!{DARK}]{PINK} Error generating QR Code: {e}{LIGHT1}")
