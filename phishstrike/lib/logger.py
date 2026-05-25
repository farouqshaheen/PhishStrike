"""
PhishStrike - Centralized Logging Module
Provides a shared logger with colored terminal output and rotating file logs.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# ─── ANSI color codes for terminal output ────────────────────────────────────
_RESET = "\033[0m"
_COLORS = {
    "DEBUG":    "\033[1;34m",   # Blue
    "INFO":     "\033[1;36m",   # Cyan
    "WARNING":  "\033[1;33m",   # Yellow
    "ERROR":    "\033[1;31m",   # Red
    "CRITICAL": "\033[1;35m",   # Magenta
}


class _ColorFormatter(logging.Formatter):
    """Adds ANSI color to log level name in terminal output."""

    def format(self, record):
        color = _COLORS.get(record.levelname, _RESET)
        record.levelname = f"{color}{record.levelname:<8}{_RESET}"
        return super().format(record)


def get_logger(name: str = "PhishStrike") -> logging.Logger:
    """
    Return a configured logger instance.
    Creates log directory and sets up both file and stream handlers on first call.

    Args:
        name: Logger namespace (default 'PhishStrike')

    Returns:
        logging.Logger: Configured logger ready to use.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ─── Ensure logs directory exists ────────────────────────────────────
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "phishstrike.log")

    # ─── File handler (rotating, max 2MB, keep 3 backups) ────────────────
    file_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = RotatingFileHandler(
        log_file, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_fmt)

    # ─── Stream (terminal) handler ────────────────────────────────────────
    stream_fmt = _ColorFormatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(stream_fmt)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
