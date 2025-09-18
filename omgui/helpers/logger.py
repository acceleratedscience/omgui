"""
Logger singleton.

Usage:
    from omgui.helpers import logger
    logger.info("Your message")
"""

import logging
from omgui.helpers.jupyter import nb_mode


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
        # print(record.__dict__)

        # Define colors
        color_start = self.LEVEL_COLORS.get(record.levelno, self.LEVEL_COLORS["RESET"])
        color_end = self.LEVEL_COLORS["RESET"]

        # ERROR/CRITICAL --> also color message
        if record.levelname in ["ERROR", "CRITICAL"]:
            record.msg = f"{color_start}{record.msg}{color_end}"

        log_message = super().format(record)

        # Find-and-replace hack to color level name after formatting
        # This is needed to have -8s spacing work correctly with ansi codes
        # See fmt below, and for further reading:
        # https://docs.python.org/3/howto/logging-cookbook.html#formatting-styles
        levelname_placeholder = record.levelname
        colored_levelname = f"{color_start}{record.levelname}{color_end}"

        return log_message.replace(levelname_placeholder, colored_levelname)


# Configure
# ------------------------------------

root = logging.getLogger()

# Avoid duplicate logs
if root.handlers:
    root.handlers.clear()


# Jupyter notebooks
if nb_mode():
    # Only print the message (no colors, no level/name)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))

    # Never print info/debug logs
    root.setLevel(logging.ERROR)

# Standard terminal
else:
    handler = logging.StreamHandler()
    fmt = "%(levelname)-8s \x1b[90m%(name)s\x1b[0m %(message)s"
    handler.setFormatter(ColoredFormatter(fmt))
    root.setLevel(logging.INFO)

root.addHandler(handler)

# Import this:
logger = logging.getLogger(__name__)
