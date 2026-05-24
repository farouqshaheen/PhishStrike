import threading

from phishstrike import state
from phishstrike.capture.monitor import capture_data


def start_background_monitor() -> None:
    state.stop_monitoring.clear()
    if not state.monitoring_thread or not state.monitoring_thread.is_alive():
        state.monitoring_thread = threading.Thread(
            target=capture_data, args=(True,), daemon=True
        )
        state.monitoring_thread.start()


def finish_attack() -> None:
    """Start silent capture and open the post-attack control menu."""
    start_background_monitor()
    from phishstrike.cli.menu import post_attack_menu

    post_attack_menu()
