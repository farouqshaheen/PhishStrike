"""Simple in-memory rate limiting for dashboard login attempts."""

import time
from collections import defaultdict

_attempts: dict[str, list[float]] = defaultdict(list)


def is_rate_limited(key: str, max_attempts: int, window_seconds: int) -> bool:
    now = time.time()
    window = _attempts[key]
    _attempts[key] = [t for t in window if now - t < window_seconds]
    return len(_attempts[key]) >= max_attempts


def record_failure(key: str) -> None:
    _attempts[key].append(time.time())


def reset(key: str) -> None:
    _attempts.pop(key, None)
