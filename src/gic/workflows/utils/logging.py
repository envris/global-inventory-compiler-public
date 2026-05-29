"""Custom logger for the project."""

import logging


def get_logger(loglevel: str = "INFO") -> logging.Logger:
    """Create a custom logger with the specified name and log level."""
    logger = logging.Logger("gic", level=loglevel)
    logger.setLevel(loglevel)
    formatter = logging.Formatter("%(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
