"""
Chart-related API routes.
"""

# Standard
import os
import json
from enum import Enum
from typing import Literal
from urllib.parse import quote, unquote


# Fast API
from fastapi import APIRouter
from fastapi import Request, HTTPException, status, Query, Body, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import (
    Response,
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
)

# Modules
import plotly.graph_objects as go

# Tools
from ..workers import chart_sampler
from ..workers.util import deep_merge, is_dates, hash_data


# Setup
# ------------------------------------

# Router
router = APIRouter()

# Set up templates and static files
templates = Jinja2Templates(directory="app/templates")


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
    hide_legend: bool | None = Query(False, description="Hide the legend in the chart"),
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
        "hide_legend": hide_legend,
        "barmode": barmode,
        "boxmode": boxmode,
    }


async def parse_input_data(
    request: Request,
    data_json: str | None,  # Data passed in the URL
    data_id: str,  # Data stored in Redis
):
    """
    Parse the input data from the URL or from Redis.
    """

    # From Redis
    if data_id:
        redis_client = request.app.state.redis
        input_data = await redis_client.get(f"input_data:{data_id}")
        input_data = json.loads(input_data)
        if not input_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chart data with ID '{data_id}' not found. It may have expired.",
            )

    # From URL
    elif data_json:
        input_data = json.loads(unquote(data_json))
        if not input_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The 'data_json' query parameter cannot be empty.",
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
    if options.get("hide_legend") is True:
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


@router.get("/r/{chart_type}", summary="Generate random data for various chart types")
async def random_data(
    request: Request,
    chart_type: ChartType | Literal["boxplot-group"],
    raw: bool | None = Query(False),
    display: bool | None = Query(False),
):
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
        chart_data = chart_sampler.boxplot(group=True)
    elif chart_type == ChartType.HISTOGRAM:
        chart_data = chart_sampler.histogram()
    else:
        return f"Invalid chart type '{chart_type}'"

    # Convert the dictionary to a URL-encode JSON string
    json_string = json.dumps(chart_data)
    encoded_data = quote(json_string)

    # Get additional query parameters (excluding the ones we already handle)
    additional_params = {}
    for key, value in request.query_params.items():
        if key not in ["raw", "display"]:
            additional_params[key] = value

    # Build additional parameters string for URL
    additional_params_str = ""
    if additional_params:
        additional_params_str = "&" + "&".join(
            [f"{k}={v}" for k, v in additional_params.items()]
        )

    # Compile URL
    chart_type = ChartType.BOXPLOT if chart_type == "boxplot-group" else chart_type
    url = f"http://localhost:8034/chart/{chart_type.value}?data={encoded_data}{additional_params_str}"

    #
    #

    # Display JSON
    if raw:
        return PlainTextResponse(json_string)

    # Display link
    elif display:
        return HTMLResponse(
            content=f"<a href='{url}' target='_blank'>{url}</a>", status_code=200
        )

    # Redirect
    else:
        return RedirectResponse(url=url)


@router.get("/data", summary="List available sample data files")
async def data_files():
    sample_data_dir = "data"
    files = os.listdir(sample_data_dir)
    files = list(
        filter(lambda f: f.startswith("sample-") and f.endswith(".json"), files)
    )
    links_str = []
    for file in files:
        # fmt: off
        link_chart = f"<a href='/data/{file}' style='text-decoration:none'>{file.replace('sample-', '')}</a>"
        link_png = f"<a href='/data/{file}?output=png' style='text-decoration:none'>png</a>"
        link_svg = f"<a href='/data/{file}?output=svg' style='text-decoration:none'>svg</a>"
        link_raw = (f"<a href='/data/{file}?raw=1' style='color:gray; text-decoration:none'>raw</a>")

        links_str.append(" / ".join([link_chart, link_png, link_svg, link_raw]))
        # fmt: on

    response_content = (
        "<h1>Sample Charts</h1><ul><li>" + "</li><li>".join(links_str) + "</li></ul>"
    )
    return HTMLResponse(content=response_content, status_code=200)


@router.get("/data/{filename}", summary="Render a chart from JSON data")
async def chart_file(
    # fmt: off
    request: Request,
    filename: str,
    raw: bool | None = Query(False),
    options: dict = Depends(query_params),
    output: Literal["png", "svg"] | None = Query(None, description="Output format: png, svg, or None for HTML"),
    # fmt: on
):

    # Load json data from file
    with open(f"data/{filename}", encoding="utf-8") as f:
        chart_data = json.load(f)
        input_data = chart_data

    if raw:
        json_string = json.dumps(chart_data, indent=2)
        return PlainTextResponse(json_string)
    else:
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


# endregion
# ------------------------------------
# region - Routes: Chart Types
# ------------------------------------


# Redis POST
@router.post(
    "/chart/{chart_type}", summary="Render different chart types from POST data"
)
async def post_chart_data(
    request: Request,
    chart_type: ChartType,
    data: list[dict] = Body(...),
):
    """
    Takes chart data from the request body, stores it in Redis,
    and returns a unique ID for the data.
    """

    unique_id = hash_data(data)

    # Store data in Redis with a 24-hour expiration
    redis_client = request.app.state.redis
    await redis_client.set(f"input_data:{unique_id}", json.dumps(data), ex=86400)

    return {"id": unique_id, "url": f"/chart/{chart_type.value}/{unique_id}"}


# Bar chart
# - - -
# https://plotly.com/javascript/bar-charts/
@router.get("/chart/bar", summary="Render a bar chart from URL data")
@router.get("/chart/bar/{data_id}", summary="Render a bar chart from Redis data")
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

    print(444, options)

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
@router.get("/chart/line", summary="Render a line chart from URL data")
@router.get("/chart/line/{data_id}", summary="Render a line chart from Redis data")
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
@router.get("/chart/scatter", summary="Render a scatter plot from URL data")
@router.get("/chart/scatter/{data_id}", summary="Render a scatter plot from Redis data")
async def chart_scatter(
    # fmt: off
    request: Request,
    data_json: str | None = Query(None, alias="data"),
    data_id: str | None = None,
    options: dict = Depends(query_params),
    output: Literal["png", "svg"] | None = Query(None, description="Output format: png, svg, or None for HTML"),
    # fmt: on
):

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
@router.get("/chart/bubble", summary="Render a bubble chart from URL data")
@router.get("/chart/bubble/{data_id}", summary="Render a bubble chart from Redis data")
async def chart_bubble(
    # fmt: off
    request: Request,
    data_json: str | None = Query(None, alias="data"),
    data_id: str | None = None,
    options: dict = Depends(query_params),
    output: Literal["png", "svg"] | None = Query(None, description="Output format: png, svg, or None for HTML"),
    # fmt: on
):

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
@router.get("/chart/pie", summary="Render a pie chart from URL data")
@router.get("/chart/pie/{data_id}", summary="Render a pie chart from Redis data")
async def chart_pie(
    request: Request,
    data_json: str | None = Query(None, alias="data"),
    data_id: str | None = None,
    options: dict = Depends(query_params),
    output: Literal["png", "svg"] | None = Query(None, description="Output format: png, svg, or None for HTML"),
    # fmt: on
):

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
@router.get("/chart/boxplot", summary="Render a box plot chart from URL data")
@router.get("/chart/boxplot/{data_id}", summary="Render a box plot chart from Redis data")
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
@router.get("/chart/histogram", summary="Render a histogram chart from URL data")
@router.get("/chart/histogram/{data_id}", summary="Render a histogram chart from Redis data")
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
