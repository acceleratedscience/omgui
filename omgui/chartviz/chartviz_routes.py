"""
Chart visualization API routes.
"""

# Std
import json
from enum import Enum
from typing import Literal
from urllib.parse import unquote


# FastAPI
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response, HTMLResponse
from fastapi import Request, HTTPException, status, Query, Body, Depends

# 3rd party
import kaleido  # We need this
import plotly.graph_objects as go

# OMGUI
from omgui import config
from omgui.util.logger import get_logger
from omgui.chartviz import chart_sampler
from omgui.util import exceptions as omg_exc
from omgui.util.general import deep_merge, is_dates, hash_data


# Setup
# ------------------------------------

# Router
chartviz_router = APIRouter()

# Set up templates and static files
templates = Jinja2Templates(directory="omgui/chartviz/templates")

# Logger
logger = get_logger()


# Types
# ------------------------------------


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


# ------------------------------------
# region - Auxiliary functions
# ------------------------------------


def query_params(
    # fmt: off
    width: int | Literal['auto'] | None = Query(None, description="Width of the chart"),
    height: int | Literal['auto'] | None = Query(None, description="Height of the chart"),
    scale: int | None = Query(None, description="PNG scale factor"),
    omit_legend: bool | None = Query(False, description="Omit the legend from the chart"),
    title: str | None = Query(None, description="Chart title"),
    subtitle: str | None = Query(None, description="Chart subtitle"),
    body: str | None = Query(None, description="Paragraph displayed in the HTML page only"),
    x_title: str | None = Query(None, description="Title for the x axis"),
    y_title: str | None = Query(None, description="Title for the y axis"),
    x_prefix: str | None = Query(None, description="Prefix for the x axis labels"),
    y_prefix: str | None = Query(None, description="Prefix for the y axis labels"),
    x_suffix: str | None = Query(None, description="Suffix for the x axis labels"),
    y_suffix: str | None = Query(None, description="Suffix for the y axis labels"),
    
    # Chart-specific options
    barmode: Literal["stack", "group", "overlay", "relative"] | None = Query(None, description="Bar mode for bar/histogram charts"),
    boxmode: Literal["group", "overlay"] | None = Query(None, description="Box mode for box plot chart"),
    # fmt: on
):
    """
    Shared query parameters for the chart routes.

    Exposed via:
        options: dict = Depends(query_params),
    """
    return {
        "width": None if width == "auto" else width,
        "height": None if height == "auto" else height,
        "scale": scale,
        "title": title,
        "subtitle": subtitle,
        "body": body,
        "x_title": x_title,
        "y_title": y_title,
        "x_prefix": x_prefix,
        "y_prefix": y_prefix,
        "x_suffix": x_suffix,
        "y_suffix": y_suffix,
        "omit_legend": omit_legend,
        "barmode": barmode,
        "boxmode": boxmode,
    }


async def parse_input_data(
    request: Request,
    data_json: str | None,  # Data passed in the URL
    data_id: str,  # Data stored in Redis
):
    """
    Parse the input data from the URL or from Redis (or in-memory fallback).
    """

    # From Redis or in-memory fallback
    if data_id:
        redis_client = request.app.state.redis
        key = f"input_data:{data_id}"

        if redis_client:
            input_data_raw = await redis_client.get(key)
            if not input_data_raw:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chart data with ID '{data_id}' not found. It may have expired.",
                )
            input_data = json.loads(input_data_raw)
        else:
            # in-memory fallback (only for dev/demo; volative and not shared between processes)
            cache = getattr(request.app.state, "in_memory_cache", {})
            input_data_raw = cache.get(key)
            if not input_data_raw:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chart data with ID '{data_id}' not found (no Redis configured).",
                )
            input_data = json.loads(input_data_raw)

    # From URL
    elif data_json:
        input_data = json.loads(unquote(data_json))
        if not input_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The 'data_json' query parameter cannot be empty.",
            )

    else:
        # Nothing provided
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No chart data provided (use 'data' param or post data to / to get an id).",
        )

    return input_data


def compile_layout(
    chart_type: ChartType, chart_data: dict = None, options: dict = None
):
    """
    Compile the Plotly layout dictionary for all charts.
    """

    options = options or {}

    # Constants
    color_text = "#777"
    color_text_dark = "#444"
    color_line = "#CCC"
    color_line_soft = "#EEE"
    family = '"IBM Plex Sans", sans-serif'
    weight = 400
    weight_bold = 600
    palette_chromatic = [
        "#CB8897",
        "#D4B0A2",
        "#DBCDA9",
        "#BFCBA8",
        "#99CACD",
        "#94ADE0",
        "#B187D8",
        "#CD8ADE",
        "#E76069",
        "#EE936D",
        "#F3BA70",
        "#D0B96F",
        "#9BB99E",
        "#9991C1",
        "#C660BF",
        "#E861C1",
    ]
    palette = []
    for i in range(0, len(palette_chromatic)):
        c = palette_chromatic[(i * 5) % len(palette_chromatic)]
        palette.append(c)
    # palette_ibm = [
    #     "#6929c4",
    #     "#1192e8",
    #     "#005d5d",
    #     "#9f1853",
    #     "#fa4d56",
    #     "#570408",
    #     "#198038",
    #     "#002d9c",
    #     "#ee538b",
    #     "#b28600",
    #     "#009d9a",
    #     "#012749",
    #     "#8a3800",
    #     "#a56eff",
    # ]

    # Base layout object
    layout = {
        "colorway": palette,
        "paper_bgcolor": "#fff",
        "plot_bgcolor": "#fff",
        # Replace auto with None to avoid unwanted Plotly default size
        "width": options["width"] if not options["width"] == "auto" else None,
        "height": options["height"] if not options["height"] == "auto" else None,
    }

    # Title and subtitle
    layout_title = {
        "title": {
            "text": options.get("title"),
            "x": 0.5,
            "xanchor": "center",
            "y": 1,
            "yanchor": "top",
            "pad": {
                "t": 40,
            },
            "yref": "container",
            "font": {
                "family": family,
                "weight": weight_bold,
                "color": color_text_dark,
            },
            "subtitle": {
                "text": options.get("subtitle"),
                "font": {
                    "family": family,
                    "weight": weight,
                    "color": color_text,
                },
            },
        },
    }

    # X/Y axis
    layout_xy = {
        "xaxis": {
            "title": {
                "text": options.get("x_title"),
                "standoff": 20,
            },
            "rangemode": "tozero",
            "rangeslider": {
                "visible": False,
            },
            "showline": True,
            "mirror": "ticks",
            "color": color_text,
            # "gridcolor": color_line_soft,
            "linecolor": color_line,
            "ticks": "outside",
            "ticklen": 5,
            "tickcolor": "rgba(0,0,0,0)",
            "tickfont": {
                "family": family,
                "weight": weight,
            },
            "tickprefix": options.get("x_prefix"),
            "ticksuffix": options.get("x_suffix"),
        },
        "yaxis": {
            "title": {
                "text": options.get("y_title"),
                "standoff": 15,
            },
            "rangemode": "tozero",
            "showline": True,
            "mirror": "ticks",
            "color": color_text,
            "gridcolor": color_line_soft,
            "linecolor": color_line,
            "ticks": "outside",
            "ticklen": 5,
            "tickcolor": "rgba(0,0,0,0)",
            "tickfont": {
                "family": family,
                "weight": weight,
            },
            "tickprefix": options.get("y_prefix"),
            "ticksuffix": options.get("y_suffix"),
        },
    }

    # Legend
    layout_legend = {
        "legend": {
            "orientation": "h",
            # "xanchor": "left",
            # "x": 0,
            "xanchor": "center",
            "x": 0.5,
            "y": 1.03,
            "yanchor": "bottom",
            "yref": "paper",
            "font": {
                "family": family,
                "weight": weight,
                "color": color_text,
            },
            "visible": True,
        },
    }

    # Hover box
    layout_hover = {
        "hovermode": "x unified",  # Show hover information for all traces at a single x-coordinate
        "hoverlabel": {
            "bordercolor": "#CCC",
            "font": {
                "color": "#777",
            },
        },
    }

    # Mode bar - unused
    layout_modebar = {
        "modebar": {
            "remove": ["zoomin", "zoomout", "lasso", "resetScale2d", "select"],
        },
    }

    # Margins
    # Default for x/y charts has optical correction for ticks and labels
    layout_margin = {
        "margin": {
            "l": 80,
            "r": 80,
            "t": 80,
            "b": 80,
        },
    }

    #
    #

    # Merge pie chart specific layout
    if chart_type == ChartType.PIE:
        layout = deep_merge(
            layout,
            {
                "margin": {
                    "l": 40,
                    "r": 40,
                    "t": 40,
                    "b": 40,
                },
            },
        )

    # Merge x/y chart specific layout
    else:
        layout = deep_merge(
            layout,
            layout_xy,
        )
        layout = deep_merge(
            layout,
            layout_margin,
        )

        # Detect & format date x-axis
        x_values = chart_data[0].get("x", []) or []
        is_date_axis = is_dates(x_values[:20]) if chart_data else False
        if is_date_axis:
            layout["xaxis"]["type"] = "date"
            layout["xaxis"]["hoverformat"] = "%d %b, %Y"

    # Set barmode for bar charts & histograms
    if chart_type in [ChartType.BAR]:
        layout["barmode"] = options.get("barmode", "group") or "group"
    elif chart_type == ChartType.HISTOGRAM:
        layout["barmode"] = options.get("barmode", "overlay") or "overlay"

    # Set boxmode for box plots
    if chart_type == ChartType.BOXPLOT:
        layout["boxmode"] = options.get("boxmode", "group")

    # Merge title options
    if options.get("title"):
        layout = deep_merge(
            layout,
            layout_title,
        )
        if options.get("subtitle"):
            layout["margin"]["t"] = 160
        else:
            layout["margin"]["t"] = 120

    # Merge legend options
    if options.get("omit_legend") is True:
        layout["legend"] = {"visible": False}
    else:
        layout = deep_merge(
            layout,
            layout_legend,
        )

    # Merge hover options
    if chart_type == ChartType.LINE:
        layout = deep_merge(
            layout,
            layout_hover,
        )

    # Merge mode bar options
    layout = deep_merge(
        layout,
        layout_modebar,
    )

    # print("\n", json.dumps(layout, indent=2), "\n")

    return layout


def _compile_template_response(
    request: Request,
    chart_data: list[dict],
    input_data: list[dict] = None,
    layout: dict = None,
    options: dict = None,
    additional_options: dict = None,
):
    """
    Shared template response for all charts.
    """

    options = options or {}

    return templates.TemplateResponse(
        "chart.jinja",
        {
            "request": request,
            "chart_data": chart_data,
            "input_data": input_data,
            "layout": layout,
            # Options
            "width": options.get("width"),
            "height": options.get("height"),
            "title": options.get("title"),
            "subtitle": options.get("subtitle"),
            "body": options.get("body"),
            # Additional options for specific charts
            **(additional_options if additional_options is not None else {}),
        },
    )


def _compile_image_response(
    chart_data: list[dict],
    layout: dict,
    options: dict,
    output: Literal["png", "svg"],
):
    """
    Compile the image response for charts.
    """

    fig = go.Figure(data=chart_data)

    # Set width and height to defaults
    layout["width"] = (
        options.get("width", 1200) if options.get("width") != "auto" else 1200
    )
    layout["height"] = (
        options.get("height", 900) if options.get("height") != "auto" else 900
    )

    # Apply layout
    fig.update_layout(layout)

    # Generate image
    if output == "png":
        img_bytes = fig.to_image(
            format="png",
            width=layout["width"],
            height=layout["height"],
            scale=options.get("scale", 1),
        )
        return Response(
            content=img_bytes,
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename='pie_chart.png'"},
        )
    elif output == "svg":
        svg_str = fig.to_image(
            format="svg", width=layout["width"], height=layout["height"]
        ).decode("utf-8")
        return Response(
            content=svg_str,
            media_type="image/svg+xml",
            headers={"Content-Disposition": "inline; filename='pie_chart.svg'"},
        )


def compile_response(
    request: Request,
    output: Literal["png", "svg"] | None,
    chart_data: list[dict],
    input_data: list[dict],
    layout: dict,
    options: dict,
):

    # Return PNG/SVG image
    if output in ["png", "svg"]:
        return _compile_image_response(
            chart_data,
            layout,
            options,
            output,
        )

    # Return HTML template
    else:
        return _compile_template_response(
            request,
            chart_data,
            input_data,
            layout,
            options,
        )


# endregion
# ------------------------------------
# region - Routes: Demonstration
# ------------------------------------


@chartviz_router.get(
    "", response_class=HTMLResponse, summary="Interactive demo UI for the charts API"
)
def demo_charts(request: Request):
    """
    Interactive HTML demo page for the Charts API.
    Provides a user interface with controls for all API parameters.
    """
    if not config.viz_deps:
        raise omg_exc.MissingDependenciesViz

    return templates.TemplateResponse("demo-charts.html", {"request": request})


@chartviz_router.get(
    "/generate/{chart_type}",
    summary="Generate random dummy data for various chart types",
)
async def random_data(
    request: Request, chart_type: ChartType | Literal["boxplot-group"]
):
    if not config.viz_deps:
        raise omg_exc.MissingDependenciesViz

    chart_data = None
    if chart_type == ChartType.SCATTER:
        chart_data = chart_sampler.scatter()
    elif chart_type == ChartType.LINE:
        chart_data = chart_sampler.line()
    elif chart_type == ChartType.BUBBLE:
        chart_data = chart_sampler.bubble()
    elif chart_type == ChartType.PIE:
        chart_data = chart_sampler.pie()
    elif chart_type == ChartType.BAR:
        chart_data = chart_sampler.bar()
    elif chart_type == ChartType.BOXPLOT:
        chart_data = chart_sampler.boxplot()
    elif chart_type == "boxplot-group":
        chart_data = chart_sampler.boxplot(group_count=3)
    elif chart_type == ChartType.HISTOGRAM:
        chart_data = chart_sampler.histogram()
    else:
        return f"Invalid chart type '{chart_type}'"

    return chart_data


# endregion
# ------------------------------------
# region - Routes: Chart Types
# ------------------------------------


# Redis POST
@chartviz_router.post(
    "/{chart_type}", summary="Render different chart types from POST data"
)
async def post_chart_data(
    request: Request,
    chart_type: ChartType,
    data: list[dict] = Body(...),
):
    """
    Takes chart data from the request body, stores it in Redis (or in-memory fallback),
    and returns a unique ID for the data.
    """
    if not config.viz_deps:
        raise omg_exc.MissingDependenciesViz

    unique_id = hash_data(data)
    key = f"input_data:{unique_id}"

    # Use Redis when available
    redis_client = request.app.state.redis
    if redis_client:
        await redis_client.set(key, json.dumps(data), ex=86400)
        logger.info("Chart data stored in Redis as '%s'", unique_id)
        return {"id": unique_id, "url": f"/{chart_type.value}/{unique_id}"}

    # In-memory fallback
    cache = getattr(request.app.state, "in_memory_cache", None)
    if cache is None:
        request.app.state.in_memory_cache = {}
        cache = request.app.state.in_memory_cache

    cache[key] = json.dumps(data)

    logger.info(
        "Chart data stored in in-memory cache as '%s' (no Redis configured)", unique_id
    )

    return {
        "id": unique_id,
        "url": f"/viz/chart/{chart_type.value}/{unique_id}",
        "note": "Data stored in in-memory cache (no expiry, not persistent). Configure REDIS_URL to enable Redis storage.",
    }


# Bar chart
# - - -
# https://plotly.com/javascript/bar-charts/
@chartviz_router.get("/bar", summary="Render a bar chart from URL data")
@chartviz_router.get("/bar/{data_id}", summary="Render a bar chart from Redis data")
async def chart_bar(
    # fmt: off
    request: Request,
    data_json: str | None = Query(None, alias="data"),
    data_id: str | None = None,
    options: dict = Depends(query_params),
    horizontal: bool = Query(False, alias="h", description="Render bar chart horizontally"),
    output: Literal["png", "svg"] | None = Query(None, description="Output format: png, svg, or None for HTML"),
    # fmt: on
):
    if not config.viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Parse data
    input_data = await parse_input_data(request, data_json, data_id)

    # Compile Plotly data dict
    chart_data = []
    for [_, ds] in enumerate(input_data):
        if horizontal:
            chart_data.append(
                {
                    "type": "bar",
                    "name": ds.get("name"),
                    "y": ds.get("keys"),
                    "x": ds.get("values"),
                    "orientation": "h",
                    # "opacity": 0.5,
                }
            )
        else:
            chart_data.append(
                {
                    "type": "bar",
                    "name": ds.get("name"),
                    "x": ds.get("keys"),
                    "y": ds.get("values"),
                    # "opacity": 0.5,
                }
            )

    # Compile Plotly layout dict
    layout = compile_layout(ChartType.BAR, chart_data, options)

    # Response
    return compile_response(
        request,
        output,
        chart_data,
        input_data,
        layout,
        options,
    )


# Line chart
# - - -
# https://plotly.com/javascript/line-charts/
@chartviz_router.get("/line", summary="Render a line chart from URL data")
@chartviz_router.get("/line/{data_id}", summary="Render a line chart from Redis data")
async def chart_line(
    # fmt: off
    request: Request,
    data_json: str | None = Query(None, alias="data"),
    data_id: str | None = None,
    options: dict = Depends(query_params),
    horizontal: bool = Query(False, alias="h", description="Render line chart horizontally"),
    output: Literal["png", "svg"] | None = Query(None, description="Output format: png, svg, or None for HTML"),
    # fmt: on
):
    if not config.viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Parse data
    input_data = await parse_input_data(request, data_json, data_id)

    # Compile Plotly data dict
    chart_data = []
    for [_, ds] in enumerate(input_data):
        if horizontal:
            chart_data.append(
                {
                    "type": "scatter",
                    "mode": "lines",
                    "name": ds.get("name"),
                    "x": ds.get("y"),
                    "y": ds.get("x"),
                }
            )
        else:
            chart_data.append(
                {
                    "type": "scatter",
                    "mode": "lines",  # <--
                    "name": ds.get("name"),
                    "x": ds.get("x"),
                    "y": ds.get("y"),
                }
            )

    # Compile Plotly layout dict
    layout = compile_layout(ChartType.LINE, chart_data, options)

    # Response
    return compile_response(
        request,
        output,
        chart_data,
        input_data,
        layout,
        options,
    )


# Scatter chart
# - - -
# https://plotly.com/javascript/line-and-scatter/
@chartviz_router.get("/scatter", summary="Render a scatter plot from URL data")
@chartviz_router.get(
    "/scatter/{data_id}", summary="Render a scatter plot from Redis data"
)
async def chart_scatter(
    # fmt: off
    request: Request,
    data_json: str | None = Query(None, alias="data"),
    data_id: str | None = None,
    options: dict = Depends(query_params),
    output: Literal["png", "svg"] | None = Query(None, description="Output format: png, svg, or None for HTML"),
    # fmt: on
):
    if not config.viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Parse data
    input_data = await parse_input_data(request, data_json, data_id)

    # Compile Plotly data dict
    chart_data = []
    for [_, ds] in enumerate(input_data):
        chart_data.append(
            {
                "type": "scatter",
                "mode": "markers",  # <--
                "name": ds.get("name"),
                "x": ds.get("x"),
                "y": ds.get("y"),
            }
        )

    # Compile Plotly layout dict
    layout = compile_layout(ChartType.SCATTER, chart_data, options)

    # Response
    return compile_response(
        request,
        output,
        chart_data,
        input_data,
        layout,
        options,
    )


# Bubble chart
# - - -
# https://plotly.com/javascript/bubble-charts/
@chartviz_router.get("/bubble", summary="Render a bubble chart from URL data")
@chartviz_router.get(
    "/bubble/{data_id}", summary="Render a bubble chart from Redis data"
)
async def chart_bubble(
    # fmt: off
    request: Request,
    data_json: str | None = Query(None, alias="data"),
    data_id: str | None = None,
    options: dict = Depends(query_params),
    output: Literal["png", "svg"] | None = Query(None, description="Output format: png, svg, or None for HTML"),
    # fmt: on
):
    if not config.viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Parse data
    input_data = await parse_input_data(request, data_json, data_id)

    # Compile Plotly data dict
    chart_data = []
    for [_, ds] in enumerate(input_data):
        chart_data.append(
            {
                "type": "scatter",
                "mode": "markers",  # <--
                "name": ds.get("name"),
                "x": ds.get("x"),
                "y": ds.get("y"),
                "marker": {"size": ds.get("size")},
            }
        )

    # Compile Plotly layout dict
    layout = compile_layout(ChartType.BUBBLE, chart_data, options)

    # Response
    return compile_response(
        request,
        output,
        chart_data,
        input_data,
        layout,
        options,
    )


# Pie chart
# - - -
# fmt: off
# https://plotly.com/javascript/pie-charts/
@chartviz_router.get("/pie", summary="Render a pie chart from URL data")
@chartviz_router.get("/pie/{data_id}", summary="Render a pie chart from Redis data")
async def chart_pie(
    request: Request,
    data_json: str | None = Query(None, alias="data"),
    data_id: str | None = None,
    options: dict = Depends(query_params),
    output: Literal["png", "svg"] | None = Query(None, description="Output format: png, svg, or None for HTML"),
    # fmt: on
):
    if not config.viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Parse data
    input_data = await parse_input_data(request, data_json, data_id)

    # Compile Plotly data dict
    chart_data = []
    for [_, ds] in enumerate(input_data):
        chart_data.append(
            {
                "type": "pie",
                "values": ds.get("values"),
                "labels": ds.get("labels"),
            }
        )

    # Compile Plotly layout dict
    layout = compile_layout(ChartType.PIE, chart_data, options)

    # Response
    return compile_response(
        request,
        output,
        chart_data,
        input_data,
        layout,
        options,
    )


# Box plot chart
# - - -
# fmt: off
# https://plotly.com/javascript/box-plots/
@chartviz_router.get("/boxplot", summary="Render a box plot chart from URL data")
@chartviz_router.get("/boxplot/{data_id}", summary="Render a box plot chart from Redis data")
async def chart_boxplot(
    request: Request,
    data_json: str | None = Query(None, alias="data"),
    data_id: str | None = None,
    options: dict = Depends(query_params),
    
    # Boxplot specific options
    horizontal: bool = Query(False, alias="h", description="Render box plot horizontally"),
    show_points: bool = Query(False, description="Show data points on the box plot"),
    boxmean: Literal[True, "True", "true", "1", False, "False", "false", "0", "sd"]
        = Query(False, description="Show mean and standard deviation on the box plot"),
    output: Literal["png", "svg"] | None = Query(None, description="Output format: png, svg, or None for HTML"),
    # fmt: on
):
    if not config.viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Parse data
    input_data = await parse_input_data(request, data_json, data_id)

    # fmt: off
    # Parse boxmean
    # Because it's a boolean OR a string, it's always parsed as a string
    boxmean = "sd" if boxmean == "sd" else True if boxmean in [True, "True", "true", "1"] else False
    # fmt: on

    # Compile Plotly data dict
    chart_data = []
    for [_, ds] in enumerate(input_data):
        # fmt: off
        x = ds.get("data") if horizontal else ds.get("groups")
        y = ds.get("data") if not horizontal else ds.get("groups")
        # fmt: on
        chart_data.append(
            {
                "type": "box",
                "name": ds.get("name"),
                "x": x,
                "y": y,
                "orientation": "h" if horizontal else "v",
                #
                # Box styling
                "line": {
                    "width": 1,
                },
                #
                # Data points
                "boxpoints": "all" if show_points else False,
                "pointpos": -2,
                "jitter": 0.3,
                "marker": {
                    "size": 3,
                    "opacity": 1,
                },
                #
                # Show mean/standard deviation
                "boxmean": boxmean,
            }
        )
    
    # Determine boxmode
    options["boxmode"] = "group" if "groups" in input_data[0] else "overlay"

    # Compile Plotly layout dict
    layout = compile_layout(ChartType.BOXPLOT, chart_data, options)

    # Response
    return compile_response(
        request,
        output,
        chart_data,
        input_data,
        layout,
        options,
    )


# Histogram chart
# - - -
# https://plotly.com/javascript/histograms/
@chartviz_router.get("/histogram", summary="Render a histogram chart from URL data")
@chartviz_router.get("/histogram/{data_id}", summary="Render a histogram chart from Redis data")
async def chart_histogram(
    # fmt: off
    request: Request,
    data_json: str | None = Query(None, alias="data"),
    data_id: str | None = None,
    options: dict = Depends(query_params),
    horizontal: bool = Query(False, alias="h", description="Render histogram chart horizontally"),
    barmode: Literal["stack", "group", "overlay", "relative"] = Query("overlay", description="Bar mode for histogram chart"),
    output: Literal["png", "svg"] | None = Query(None, description="Output format: png, svg, or None for HTML"),
    # fmt: on
):
    if not config.viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Parse data
    input_data = await parse_input_data(request, data_json, data_id)

    # Compile Plotly data dict
    chart_data = []
    for [_, ds] in enumerate(input_data):
        if horizontal:
            chart_data.append(
                {
                    "type": "histogram",
                    "name": ds.get("name"),
                    "y": ds.get("values"),
                    "opacity": 1 if barmode == "stack" else 0.5,
                }
            )
        else:
            chart_data.append(
                {
                    "type": "histogram",
                    "name": ds.get("name"),
                    "x": ds.get("values"),
                    "opacity": 1 if barmode == "stack" else 0.5,
                }
            )

    # Compile Plotly layout dict
    layout = compile_layout(ChartType.HISTOGRAM, chart_data, options)

    # Response
    return compile_response(
        request,
        output,
        chart_data,
        input_data,
        layout,
        options,
    )


# endregion
# ------------------------------------
