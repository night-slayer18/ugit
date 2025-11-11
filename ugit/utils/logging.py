"""
Logging utilities for ugit.

Provides a centralized logging system to replace print statements
and improve error tracking and debugging.
"""

import logging
import sys
from typing import Optional

# Create module-level logger
_logger: Optional[logging.Logger] = None


def get_logger(name: str = "ugit") -> logging.Logger:
    """
    Get or create the ugit logger instance.

    Args:
        name: Logger name (default: "ugit")

    Returns:
        Configured logger instance
    """
    global _logger
    if _logger is None:
        _logger = logging.getLogger(name)
        _logger.setLevel(logging.INFO)

        # Avoid adding multiple handlers
        if not _logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setLevel(logging.INFO)

            formatter = logging.Formatter(
                "%(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            _logger.addHandler(handler)

    return _logger


def set_log_level(level: int) -> None:
    """
    Set the logging level for ugit.

    Args:
        level: Logging level (logging.DEBUG, logging.INFO, etc.)
    """
    logger = get_logger()
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def set_verbose(verbose: bool) -> None:
    """
    Enable or disable verbose logging.

    Args:
        verbose: If True, enable DEBUG level logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    set_log_level(level)
