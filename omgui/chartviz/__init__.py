# Std
import inspect
from typing import Callable
from functools import wraps

# 3rd party
from IPython.display import Image, SVG, display

# OMGUI
from omgui.chartviz import render
from omgui.util.jupyter import nb_mode
from omgui.chartviz.types import ChartDataType, OutputType, BarModeType, BoxMeanType
from omgui.chartviz import defaults


# ------------------------------------
# region - Common Options Decorator
# ------------------------------------


# pylint: disable=unused-argument
def _common_params(
    *,  # Force keyword-only arguments
    title: str | None = defaults.TITLE,
    subtitle: str | None = defaults.SUBTITLE,
    body: str | None = defaults.BODY,
    x_title: str | None = defaults.X_TITLE,
    y_title: str | None = defaults.Y_TITLE,
    x_prefix: str | None = defaults.X_PREFIX,
    y_prefix: str | None = defaults.Y_PREFIX,
    x_suffix: str | None = defaults.X_SUFFIX,
    y_suffix: str | None = defaults.Y_SUFFIX,
    width: int = defaults.WIDTH,
    height: int = defaults.HEIGHT,
    scale: float = defaults.SCALE,
    omit_legend: bool = defaults.OMIT_LEGEND,
    return_data: bool = defaults.RETURN_DATA,
):
    """
    Common parameters for chart rendering functions.

    Args:
        title        (str, optional):    Title of the chart.
        subtitle     (str, optional):    Subtitle of the chart.
        body         (str, optional):    Additional descriptive text below the chart. Only used with output='html'.
        x_title      (str, optional):    Title for the x-axis.
        y_title      (str, optional):    Title for the y-axis.
        x_prefix     (str, optional):    Prefix for x-axis tick labels, eg. "€".
        y_prefix     (str, optional):    Prefix for y-axis tick labels, eg. "€".
        x_suffix     (str, optional):    Suffix for x-axis tick labels, eg. "%".
        y_suffix     (str, optional):    Suffix for y-axis tick labels, eg. "%".
        width        (int, optional):    Width of the chart in pixels.
        height       (int, optional):    Height of the chart in pixels.
        scale        (float, optional):  Scaling factor for the png pixel output. Set to 2 for high-resolution displays. Only used when output='png'.
        omit_legend  (bool, optional):   If True, do not display the legend.
        return_data  (bool, optional):   Whether to return raw data (True) or display svg/png (False) in Jupyter Notebook.
    """
    # This function is never called, it only provides the shared options
    # signature and documentation. See @with_common_options decorator below.


# @decorator
def with_common_params(func: Callable) -> Callable:
    """
    Decorator that combines the function's signature with common_params'
    signature for documentation, and handles argument separation at runtime.

    This applies the common parameters to every chart function.
    """

    # Get signatures
    common_sig = inspect.signature(_common_params)
    func_sig = inspect.signature(func)

    # Combine parameters
    new_parameters = list(func_sig.parameters.values()) + list(
        common_sig.parameters.values()
    )

    # # Debug: Print the new combined parameters
    # for p in new_parameters:
    #     print(f"{p.name:15} {p.kind}")

    # Create the new signature object
    new_signature = inspect.Signature(new_parameters)

    @wraps(func)
    def wrapper(*args: any, **kwargs: any) -> any:
        # Bind incoming args/kwargs to the new,
        # combined signature and apply defaults
        bound_args = new_signature.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Function arguments: 'data', 'horizontal', etc.
        # Common arguments: become the 'options' dict
        func_args = {}
        common_options = {}

        # Separate the arguments based on where they were defined (func vs common)
        for name, value in bound_args.arguments.items():
            if name in func_sig.parameters:
                func_args[name] = value
            elif value is not None:
                common_options[name] = value

        # Ensure 'data' and 'output' are always first,
        # remove 'options' to avoid doubling in func_args
        data = func_args.pop("data")
        output = func_args.pop("output", None)
        func_args.pop("options", None)

        # Call the original function with the transformed arguments
        return func(data, output, common_options, **func_args)

    # Assign the new signature for documentation
    wrapper.__signature__ = new_signature
    return wrapper


# endregion
# ------------------------------------
# region - Chart Functions
# ------------------------------------


def _handle_result(result: any, output: OutputType, return_data: bool = False):
    """
    Handles the result based on the output type and environment.

    In Jupyter Notebook, SVGs or PNGs are displayed directly,
    unless return_data is True. URL is always returned as is.
    """
    # Jupyter notebook display
    if nb_mode() and not return_data:
        if output == "png":
            display(Image(result))
        elif output == "svg":
            display(SVG(result))
        elif output == "url":
            return result

    # Raw return
    else:
        return result


@with_common_params
def bar(  # pylint: disable=disallowed-name
    data: ChartDataType,
    output: OutputType = defaults.OUTPUT,
    options: dict | None = defaults.OPTIONS,
    ##
    horizontal: bool = defaults.HORIZONTAL,
):
    """
    Render a bar chart from input data.
    """
    result = render.bar(data, output, options, horizontal)
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


@with_common_params
def line(
    data: ChartDataType,
    output: OutputType = defaults.OUTPUT,
    options: dict | None = defaults.OPTIONS,
    ##
    horizontal: bool = defaults.HORIZONTAL,
):
    """
    Render a line chart from input data.
    """
    result = render.line(data, output, options, horizontal)
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


@with_common_params
def scatter(
    data: ChartDataType,
    output: OutputType = defaults.OUTPUT,
    options: dict | None = defaults.OPTIONS,
):
    """
    Render a scatter plot from input data.
    """
    result = render.scatter(data, output, options)
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


@with_common_params
def bubble(
    data: ChartDataType,
    output: OutputType = defaults.OUTPUT,
    options: dict | None = defaults.OPTIONS,
):
    """
    Render a bubble chart from input data.
    """
    result = render.bubble(data, output, options)
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


@with_common_params
def pie(
    data: ChartDataType,
    output: OutputType = defaults.OUTPUT,
    options: dict | None = defaults.OPTIONS,
):
    """
    Render a pie chart from input data.
    """
    result = render.pie(data, output, options)
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


@with_common_params
def boxplot(
    data: ChartDataType,
    output: OutputType = defaults.OUTPUT,
    options: dict | None = defaults.OPTIONS,
    ##
    horizontal: bool = False,
    show_points: bool = False,
    boxmean: BoxMeanType = False,
):
    """
    Render a boxplot from input data.
    """
    result = render.boxplot(data, output, options, horizontal, show_points, boxmean)
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


@with_common_params
def histogram(
    data: ChartDataType,
    output: OutputType = defaults.OUTPUT,
    options: dict | None = defaults.OPTIONS,
    ##
    horizontal: bool = defaults.HORIZONTAL,
    barmode: BarModeType = defaults.BARMODE,
):
    """
    Render a histogram chart from input data.
    """
    result = render.histogram(data, output, options, horizontal, barmode)
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


# endregion
# ------------------------------------
