"""
Default values for chartviz functions.
"""

from omgui.chartviz.types import OutputType, BarModeType

# Main
OUTPUT: OutputType = "svg"
OPTIONS: dict = None

# Shared options
TITLE = None
SUBTITLE = None
BODY = None
X_TITLE = None
Y_TITLE = None
X_PREFIX = None
Y_PREFIX = None
X_SUFFIX = None
Y_SUFFIX = None
WIDTH = 600
HEIGHT = 400
SCALE = 1.0
OMIT_LEGEND = True
RETURN_DATA = False

# Function-specific options
HORIZONTAL = False
BARMODE: BarModeType = "overlay"
