"""Notify the live dashboard when new capture data is available."""

import urllib.error
import urllib.request

from config import Config


def notify_dashboard_refresh(timeout: float = 1.0) -> bool:
    """
    Ping the dashboard internal refresh endpoint (no browser session required).
    Returns True if the dashboard acknowledged the request.
    """
    url = (
        f"http://127.0.0.1:{Config.DASHBOARD_PORT}/api/internal/refresh"
    )
    req = urllib.request.Request(
        url,
        method="POST",
        headers={"X-Internal-Key": Config.internal_api_key()},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError, TimeoutError):
        return False
