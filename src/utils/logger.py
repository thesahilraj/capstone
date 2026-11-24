"""Centralized structured logging utility with console and rotating file support."""

import os
import logging
from typing import Optional

_LOGGER: Optional[logging.Logger] = None

def get_logger(name: str = "OS-SimSuite", log_file: Optional[str] = None) -> logging.Logger:
    """Retrieve or initialize the centralized application logger."""
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Avoid duplicate handlers if re-initialized
    if not logger.handlers:
        # Formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s:%(funcName)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console Handler (INFO level)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        ch.setFormatter(console_formatter)
        logger.addHandler(ch)

        # File Handler (DEBUG level)
        if log_file is None:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output", "traces")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "simsuite.log")

        try:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception as e:
            logger.warning(f"Failed to create file logger at {log_file}: {e}")

    _LOGGER = logger
    return _LOGGER
