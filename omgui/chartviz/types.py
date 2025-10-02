from enum import Enum
from typing import Literal


class ChartType(Enum):
    """
    Supported chart types
    More available: https://plotly.com/javascript/#basic-charts
    """

    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    PIE = "pie"
    BOXPLOT = "boxplot"
    HISTOGRAM = "histogram"


# Function parameters - main
ChartDataType = list[dict[str, str | list[str] | list[float]]]
OutputType = Literal["html", "png", "svg", "url"]
OptionsType = dict[str, str | int | float | bool]
# Function parameters - specific
BarModeType = Literal["stack", "group", "overlay", "relative"]
BoxMeanType = Literal[True, "True", "true", "1", False, "False", "false", "0", "sd"]
