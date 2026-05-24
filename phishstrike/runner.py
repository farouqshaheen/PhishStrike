"""Application bootstrap and main entry point."""

import signal
import sys

from lib.terminal_ui import DARK, WHITE, reset_color


def _configure_stdio() -> None:
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass


def _sig_handler(sig, frame):
    print(f"\n\n{DARK}[{WHITE}!{DARK}]{DARK} Program Interrupted.")
    reset_color()
    sys.exit(0)


def _ensure_dependencies() -> None:
    """Import required packages; exit with install instructions if any are missing."""
    try:
        import bcrypt  # noqa: F401
        import qrcode  # noqa: F401
        import database  # noqa: F401
        from lib import ai_assistant  # noqa: F401
        from lib import site_injector  # noqa: F401
        from lib.dashboard_client import notify_dashboard_refresh  # noqa: F401
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
            "\033[1;38;2;0;255;255m    WSL/Kali     : pip3 install -r requirements.txt --break-system-packages\033[0m"
        )
        print(
            "\033[1;38;2;0;255;255m    Termux       : pip install -r requirements.txt\033[0m"
        )
        sys.exit(1)


def main() -> None:
    _configure_stdio()
    signal.signal(signal.SIGINT, _sig_handler)
    signal.signal(signal.SIGTERM, _sig_handler)

    _ensure_dependencies()

    from lib.network import (
        check_status,
        dependencies,
        install_cloudflared,
        install_localxpose,
        kill_pid,
        setup_env,
    )
    from phishstrike.cli.dashboard import start_dashboard
    from phishstrike.cli.menu import main_menu

    kill_pid()
    dependencies()
    check_status()
    setup_env()

    install_cloudflared()
    install_localxpose()
    start_dashboard()
    main_menu()
