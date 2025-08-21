# ------------------------------------
# region - Imports
# ------------------------------------

# Fast API
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Query, Request, Depends
from fastapi.responses import (
    Response,
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
)

# Modules
import os
import json
import logging
from enum import Enum
from io import BytesIO
from cairosvg import svg2png
from pydantic import BaseModel
import plotly.graph_objects as go
from typing import Optional, Literal
from urllib.parse import quote, unquote

# Tools
from workers import svgmol_2d, svgmol_3d, sampler
from workers.util import deep_merge

# Color palette for charts
palette_rgb = [
    # v1
    # (204, 129, 130),
    # (204, 173, 129),
    # (203, 204, 127),
    # (174, 204, 129),
    # (129, 204, 173),
    # (129, 173, 204),
    # (173, 129, 204),
    # (203, 129, 205),
    # v2 - color shift
    # (216, 129, 150),
    # (220, 173, 155),
    # (223, 204, 158),
    # (189, 204, 158),
    # (139, 204, 208),
    # (138, 173, 239),
    # (183, 129, 235),
    # (216, 129, 239),
    #
    # Desat
    (203, 136, 151),
    (212, 176, 162),
    (219, 205, 169),
    (191, 203, 168),
    (153, 202, 205),
    (148, 173, 224),
    (177, 135, 216),
    (205, 138, 222),
    #
    # Full color
    (231, 96, 105),
    (238, 147, 109),
    (243, 186, 112),
    (208, 185, 111),
    (155, 185, 158),
    (153, 145, 193),
    (198, 96, 191),
    (232, 97, 193),
]

palette_trash = [
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


# endregion
# ------------------------------------
# region - Setup
# ------------------------------------


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Molecule Visualization API using RDKit",
    version="1.0.0",
    description="Returns 2D visualizations of molecules in SVG format using RDKit.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up templates and static files
templates = Jinja2Templates(directory="templates")

# Mount static files directory if needed
app.mount("/static", StaticFiles(directory="static"), name="static")


class SmilesPayload(BaseModel):
    smiles: str


class ChartType(Enum):
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    PIE = "pie"
    BOXPLOT = "boxplot"
    HISTOGRAM = "histogram"


# endregion
# ------------------------------------
# region - Routes: General
# ------------------------------------


# Examples
@app.get("/", summary="Example links")
def examples():
    response = [
        "<a href='/demo/molecules'><button>Interactive molecule demo</button></a><br>",
        "<a href='/demo/charts'><button>Interactive chart demo</button></a>",
        "",
        "<b>Molecule examples:</b>",
        "<a href='/molecule/CC(=O)OC1=CC=CC=C1C(=O)O'>2D example A (Aspirin)</a>",
        "<a href='/molecule/CN1C=NC2=C1C(=O)N(C(=O)N2C)C'>2D example B (Caffeine)</a>",
        "<a href='/molecule/Clc1cc(Cl)c(Cl)c(-c2c(Cl)c(Cl)cc(Cl)c2Cl)c1Cl'>2D example C (PCB 202)</a>",
        "",
        "<a href='/molecule/CC(=O)OC1=CC=CC=C1C(=O)O?d3=1'>3D example A (Aspirin)</a>",
        "<a href='/molecule/CN1C=NC2=C1C(=O)N(C(=O)N2C)C?d3=1'>3D example B (Caffeine)</a>",
        "<a href='/molecule/Clc1cc(Cl)c(Cl)c(-c2c(Cl)c(Cl)cc(Cl)c2Cl)c1Cl?d3=1'>3D example C (PCB 202)</a>",
    ]
    response_str = "<br>".join(response)
    return Response(content=response_str, media_type="text/html")


# Demo page - molecules
@app.get(
    "/demo/molecules",
    response_class=HTMLResponse,
    summary="Interactive demo UI for the molecules API",
)
def demo_molecules(request: Request):
    """
    Interactive HTML demo page for the Molecule Visualization API.
    Provides a user interface with controls for all API parameters.
    """
    return templates.TemplateResponse("demo-molecules.html", {"request": request})


# Demo page - charts
@app.get(
    "/demo/charts",
    response_class=HTMLResponse,
    summary="Interactive demo UI for the charts API",
)
def chart_molecules(request: Request):
    """
    Interactive HTML demo page for the Charts API.
    Provides a user interface with controls for all API parameters.
    """
    return templates.TemplateResponse("demo-charts.html", {"request": request})


# endregion
# ------------------------------------
# region - Routes: Molecules
# ------------------------------------


# Smiles as query parameter
@app.get("/molecule/{smiles}", summary="Visualize any molecule from a SMILES string")
def visualize_molecule(
    # Input
    smiles: str,
    # Options
    png: bool = Query(
        False, description="Render as PNG if True, otherwise render as SVG"
    ),
    width: int = Query(800, description="Width of the rendered image in pixels"),
    height: int = Query(600, description="Height of the rendered image in pixels"),
    highlight: str = Query(
        None, description="SMARTS substructure to highlight in the molecule"
    ),
    d3: bool = Query(False, description="Render in 3D if True, otherwise render in 2D"),
    # 3D options
    d3_style: Literal["SPACEFILLING", "BALL_AND_STICK", "TUBE", "WIREFRAME"] = Query(
        "BALL_AND_STICK", description="3D rendering style"
    ),
    d3_look: Literal["CARTOON", "GLOSSY"] = Query(
        "CARTOON", description="3D rendering look"
    ),
    d3_rot_x: Optional[float] = Query(
        None, description="Rotation around x-axis in units of 60 degrees"
    ),
    d3_rot_y: Optional[float] = Query(
        None, description="Rotation around y-axis in units of 60 degrees"
    ),
    d3_rot_z: Optional[float] = Query(
        None, description="Rotation around z-axis in units of 60 degrees"
    ),
    d3_rot_random: bool = Query(
        True, description="Random rotation per axis if no rotation angles are provided"
    ),
):
    """
    Render an image of a small molecule from a SMILES string provided as query parameter.

    Examples:
    http://localhost:8034/?smiles=C1=CC=CC=C1
    """

    # Render molecule SVG
    if d3 is True:
        svg_str = svgmol_3d.render(
            smiles,
            width=width,
            height=height,
            highlight=highlight,
            #
            style=d3_style,
            look=d3_look,
            rot_random=d3_rot_random,
            rot_x=d3_rot_x,
            rot_y=d3_rot_y,
            rot_z=d3_rot_z,
        )
    else:
        svg_str = svgmol_2d.render(
            smiles,
            width=width,
            height=height,
            highlight=highlight,
        )

    # Fail
    if svg_str is None:
        logger.info(f"ERROR generating SVG for SMILES: {smiles}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid SMILES string, unable to generate SVG: {smiles}",
        )

    # Success
    logger.info(f"Success generating SVG for SMILES: {smiles}")
    logger.info(f"\nSVG:\n---\n{svg_str}")

    # Return as PNG
    if png:
        png_data = BytesIO()
        svg2png(bytestring=svg_str.encode("utf-8"), write_to=png_data)
        png_data.seek(0)  # Rewind to the beginning of the BytesIO object

        return Response(
            content=png_data.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": f'inline; filename="{smiles}.png"'},
        )

    # Return as SVG
    return Response(
        content=svg_str,
        media_type="image/svg+xml",
        headers={"Content-Disposition": f'inline; filename="{smiles}.svg"'},
    )


# endregion
# ------------------------------------
# region - Chart functions
# ------------------------------------


def chart_options(
    # fmt: off
    width: Optional[int] | Literal['auto'] = Query(None, description="Width of the chart"),
    height: Optional[int] | Literal['auto'] = Query(None, description="Height of the chart"),
    title: Optional[str] = Query(None, description="Chart title"),
    subtitle: Optional[str] = Query(None, description="Chart subtitle"),
    body: Optional[str] = Query(None, description="Paragraph displayed in the HTML page only"),
    x_title: Optional[str] = Query(None, description="Title for the x axis"),
    y_title: Optional[str] = Query(None, description="Title for the y axis"),
    x_prefix: Optional[str] = Query(None, description="Prefix for the x axis labels"),
    y_prefix: Optional[str] = Query(None, description="Prefix for the y axis labels"),
    x_suffix: Optional[str] = Query(None, description="Suffix for the x axis labels"),
    y_suffix: Optional[str] = Query(None, description="Suffix for the y axis labels"),
    hide_legend: Optional[bool] = Query(False, description="Hide the legend in the chart"),
    
    # Chart-specific options
    barmode: Optional[Literal["stack", "group", "overlay", "relative"]] = Query(None, description="Bar mode for bar/histogram charts"),
    boxmode: Optional[Literal["group", "overlay"]] = Query(None, description="Box mode for box plot chart"),
    # fmt: on
):
    """
    Shared query parameters for the chart routes.

    Exposed via:
        options: dict = Depends(chart_options),
    """
    return {
        "width": width,
        "height": height,
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


def compile_layout(chart_type: ChartType, options: dict = {}):
    """
    Compile the Plotly layout dictionary for all charts.
    """

    # Constants
    color_text = "#777"
    color_text_dark = "#444"
    color_line = "#CCC"
    color_line_soft = "#EEE"
    family = '"IBM Plex Sans", sans-serif'
    weight = 400
    weight_bold = 600
    palette_1 = [
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
    # while len(palette) < len(palette_1):
    palette = []
    for i in range(0, len(palette_1)):
        c = palette_1[(i * 5) % len(palette_1)]
        palette.append(c)

    # Base layout object
    layout = {
        "colorway": palette,
        "paper_bgcolor": "#fff",
        "plot_bgcolor": "#fff",
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
            "ticklen": 5,
            "tickcolor": "rgba(0,0,0,0)",
            "tickfont": {
                "family": family,
                "weight": weight,
            },
            "hoverformat": "%d %b, %Y",
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
    if options.get("hide_legend") is not True:
        layout = deep_merge(
            layout,
            layout_legend,
        )

    print("\n", json.dumps(layout, indent=2), "\n")

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

    if options is None:
        options = {}

    return templates.TemplateResponse(
        "chart.jinja",
        {
            "request": request,
            "chart_data": chart_data,
            "input_data": input_data,
            "layout": layout,
            "palette": palette_trash,
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

    # Apply layout
    fig.update_layout(layout)

    # Parse width and height or set defaults
    width = options.get("width", 1200) if options.get("width") != "auto" else 1200
    height = options.get("height", 800) if options.get("height") != "auto" else 800

    # Generate image
    if output == "png":
        img_bytes = fig.to_image(format="png", width=width, height=height)
        return Response(
            content=img_bytes,
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename='pie_chart.png'"},
        )
    elif output == "svg":
        svg_str = fig.to_image(format="svg", width=width, height=height).decode("utf-8")
        return Response(
            content=svg_str,
            media_type="image/svg+xml",
            headers={"Content-Disposition": "inline; filename='pie_chart.svg'"},
        )


def compile_response(
    request: Request,
    output: Optional[Literal["png", "svg"]],
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
# region - Routes: Charts
# ------------------------------------


@app.get("/r/{chart_type}", summary="Generate random data for various chart types")
async def random_data(
    request: Request,
    chart_type: ChartType | Literal["boxplot-group"],
    raw: Optional[bool] = Query(False),
    display: Optional[bool] = Query(False),
):
    chart_data = None
    if chart_type == ChartType.SCATTER:
        chart_data = sampler.scatter()
    elif chart_type == ChartType.LINE:
        chart_data = sampler.line()
    elif chart_type == ChartType.BUBBLE:
        chart_data = sampler.bubble()
    elif chart_type == ChartType.PIE:
        chart_data = sampler.pie()
    elif chart_type == ChartType.BAR:
        chart_data = sampler.bar()
    elif chart_type == ChartType.BOXPLOT:
        chart_data = sampler.boxplot()
    elif chart_type == "boxplot-group":
        chart_data = sampler.boxplot(group=True)
    elif chart_type == ChartType.HISTOGRAM:
        chart_data = sampler.histogram()
    else:
        return f"Invalid chart type '{chart_type}'"

    # Convert the dictionary to a URL-encode JSON string
    json_string = json.dumps(chart_data, indent=2)
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


@app.get("/data", summary="List available sample data files")
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


@app.get("/data/{filename}", summary="Render a chart from JSON data")
async def chart_file(
    request: Request,
    filename: str,
    raw: Optional[bool] = Query(False),
    options: dict = Depends(chart_options),
    output: Optional[Literal["png", "svg"]] = Query(
        None, description="Output format: png, svg, or None for HTML"
    ),
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
        layout = compile_layout(ChartType.BAR, options)

        # Response
        return compile_response(
            request,
            output,
            chart_data,
            input_data,
            layout,
            options,
        )


# Bar chart
# - - -
# https://plotly.com/javascript/bar-charts/
@app.get("/chart/bar", summary="Render a bar chart from URL data")
async def chart_bar(
    request: Request,
    data_json: str = Query(..., alias="data"),
    options: dict = Depends(chart_options),
    horizontal: bool = Query(
        False, alias="h", description="Render bar chart horizontally"
    ),
    output: Optional[Literal["png", "svg"]] = Query(
        None, description="Output format: png, svg, or None for HTML"
    ),
):

    # Parse URL params
    input_data = json.loads(unquote(data_json))

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
    layout = compile_layout(ChartType.BAR, options)

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
@app.get("/chart/line", summary="Render a line chart from URL data")
async def chart_line(
    request: Request,
    data_json: str = Query(..., alias="data"),
    options: dict = Depends(chart_options),
    horizontal: bool = Query(
        False, alias="h", description="Render line chart horizontally"
    ),
    output: Optional[Literal["png", "svg"]] = Query(
        None, description="Output format: png, svg, or None for HTML"
    ),
):
    # Parse URL params
    input_data = json.loads(unquote(data_json))

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
    layout = compile_layout(ChartType.LINE, options)

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
@app.get("/chart/scatter", summary="Render a line chart from URL data")
async def chart_scatter(
    request: Request,
    data_json: str = Query(..., alias="data"),
    options: dict = Depends(chart_options),
    output: Optional[Literal["png", "svg"]] = Query(
        None, description="Output format: png, svg, or None for HTML"
    ),
):

    # Parse URL params
    input_data = json.loads(unquote(data_json))

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
    layout = compile_layout(ChartType.SCATTER, options)

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
@app.get("/chart/bubble", summary="Render a bubble chart from URL data")
async def chart_bubble(
    request: Request,
    data_json: str = Query(..., alias="data"),
    options: dict = Depends(chart_options),
    output: Optional[Literal["png", "svg"]] = Query(
        None, description="Output format: png, svg, or None for HTML"
    ),
):

    # Parse URL params
    input_data = json.loads(unquote(data_json))

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
    layout = compile_layout(ChartType.BUBBLE, options)

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
# https://plotly.com/javascript/pie-charts/
@app.get("/chart/pie", summary="Render a pie chart from URL data")
async def chart_pie(
    request: Request,
    data_json: str = Query(..., alias="data"),
    options: dict = Depends(chart_options),
    output: Optional[Literal["png", "svg"]] = Query(
        None, description="Output format: png, svg, or None for HTML"
    ),
):

    # Parse URL params
    input_data = json.loads(unquote(data_json))

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
    layout = compile_layout(ChartType.PIE, options)

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
# https://plotly.com/javascript/box-plots/
@app.get("/chart/boxplot", summary="Render a box plot chart from URL data")
async def chart_boxplot(
    request: Request,
    data_json: str = Query(..., alias="data"),
    options: dict = Depends(chart_options),
    # Boxplot specific options
    horizontal: bool = Query(
        False, alias="h", description="Render box plot horizontally"
    ),
    show_points: bool = Query(False, description="Show data points on the box plot"),
    boxmean: Literal[
        True, "True", "true", "1", False, "False", "false", "0", "sd"
    ] = Query(False, description="Show mean and standard deviation on the box plot"),
    output: Optional[Literal["png", "svg"]] = Query(
        None, description="Output format: png, svg, or None for HTML"
    ),
):

    # Parse URL params
    input_data = json.loads(unquote(data_json))

    # Parse boxmean
    # fmt: off
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
    options["boxmode"] = "group" if "groups" in data_json else "overlay"

    # Compile Plotly layout dict
    layout = compile_layout(ChartType.BOXPLOT, options)

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
@app.get("/chart/histogram", summary="Render a histogram chart from URL data")
async def chart_histogram(
    request: Request,
    data_json: str = Query(..., alias="data"),
    options: dict = Depends(chart_options),
    horizontal: bool = Query(
        False, alias="h", description="Render histogram chart horizontally"
    ),
    barmode: Literal["stack", "group", "overlay", "relative"] = Query(
        "overlay", description="Bar mode for histogram chart"
    ),
    output: Optional[Literal["png", "svg"]] = Query(
        None, description="Output format: png, svg, or None for HTML"
    ),
):

    # Parse URL params
    input_data = json.loads(unquote(data_json))

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
    layout = compile_layout(ChartType.HISTOGRAM, options)

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


#
#
#
#
#
#


# @app.get("/chart/png", summary="Return a PNG image of a chart from JSON data.")
# async def chart_png(
#     data: str,
#     width: int = 1000,
#     height: int = 750,
#     title: str = None,
#     #
#     # PNG parameters
#     scale: int = 1,
# ):
#     data = quote(data)
#     html_url = f"http://localhost:8034/chart?width={width}&height={height}&title={title}&data={data}"
#     png_bytes = await screenshot(html_url, scale=scale)

#     return StreamingResponse(
#         BytesIO(png_bytes),
#         media_type="image/png",
#     )
