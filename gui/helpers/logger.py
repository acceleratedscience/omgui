"""
Logger singleton.

Usage:
    from helpers import logger
    logger.info("Your message")
"""

import logging


# Define format
class ColoredFormatter(logging.Formatter):
    """
    Custom formatter for colored logging output.
    """

    # fmt: off
    LEVEL_COLORS = {
        logging.DEBUG: "\x1b[90m",      # bright black / gray
        logging.INFO: "\x1b[32m",       # green
        logging.WARNING: "\x1b[33m",    # yellow
        logging.ERROR: "\x1b[31m",      # red
        logging.CRITICAL: "\x1b[41m",   # red background
        "RESET": "\x1b[0m",             # reset color
    }
    # fmt: on

    def format(self, record):
        color_start = self.LEVEL_COLORS.get(record.levelno, self.LEVEL_COLORS["RESET"])
        color_end = self.LEVEL_COLORS["RESET"]
        log_message = super().format(record)
        placeholder = f" {record.levelname} "
        colored_levelname = f"{color_start}{record.levelname}{color_end}"
        return log_message.replace(placeholder, f" {colored_levelname} ")


# Configure
root = logging.getLogger()
root.setLevel(logging.INFO)

# Avoid duplicate logs
if root.handlers:
    root.handlers.clear()

# Initialize
handler = logging.StreamHandler()
fmt = "\x1b[90m---------\x1b[0m %(levelname)-8s \x1b[90m%(name)s\x1b[0m %(message)s"
handler.setFormatter(ColoredFormatter(fmt))
root.addHandler(handler)

# Import this:
logger = logging.getLogger(__name__)
