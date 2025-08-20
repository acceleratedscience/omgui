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
    StreamingResponse,
    PlainTextResponse,
    RedirectResponse,
)

# Modules
import os
import json
import logging
from io import BytesIO
from cairosvg import svg2png
from pydantic import BaseModel
from typing import Optional, Literal
from urllib.parse import quote, unquote

# Tools
from workers import svgmol_2d, svgmol_3d, sampler, screenshot

# Color palette for charts
palette = [
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
    # fmt: on
):
    """
    Shared chart options from query parameters.
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
    }


def compile_template_response(
    request: Request,
    chart_data: list[dict],
    input_data: list[dict] = None,
    options: dict = {},
    additional_options: dict = None,
):
    """
    Shared template response for all charts.
    """

    return templates.TemplateResponse(
        "chart.jinja",
        {
            "request": request,
            "input_data": input_data,
            "chart_data": chart_data,
            "palette": palette,
            # Options
            "width": options.get("width"),
            "height": options.get("height"),
            "title": options.get("title"),
            "subtitle": options.get("subtitle"),
            "body": options.get("body"),
            "x_title": options.get("x_title"),
            "y_title": options.get("y_title"),
            "x_prefix": options.get("x_prefix"),
            "y_prefix": options.get("y_prefix"),
            "x_suffix": options.get("x_suffix"),
            "y_suffix": options.get("y_suffix"),
            # Additional options for specific charts
            **(additional_options if additional_options is not None else {}),
        },
    )


# endregion
# ------------------------------------
# region - Routes: Charts
# ------------------------------------


@app.get("/r/{chart_type}", summary="Generate random data for various chart types")
async def random_data(
    request: Request,
    chart_type: str,
    raw: Optional[bool] = Query(False),
    display: Optional[bool] = Query(False),
):

    chart_data = None
    if chart_type == "scatter":
        chart_data = sampler.scatter()
    elif chart_type == "line":
        chart_data = sampler.line()
    elif chart_type == "bubble":
        chart_data = sampler.bubble()
    elif chart_type == "pie":
        chart_data = sampler.pie()
    elif chart_type == "bar":
        chart_data = sampler.bar()
    elif chart_type == "boxplot":
        chart_data = sampler.boxplot()
    elif chart_type == "boxplot-group":
        chart_data = sampler.boxplot(group=True)
    elif chart_type == "histogram":
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
    chart_type = "boxplot" if chart_type == "boxplot-group" else chart_type
    url = f"http://localhost:8034/chart/{chart_type}?data={encoded_data}{additional_params_str}"

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
    barmode: Literal["stack", "group", "overlay", "relative"] = Query(
        "group", description="Bar mode for bar chart"
    ),
):

    # Parse URL params
    input_data = json.loads(unquote(data_json))

    # Compile Plotly data object
    chart_data = []
    for [_, ds] in enumerate(input_data):
        if horizontal:
            chart_data.append(
                {
                    "type": "bar",
                    "name": ds["name"],
                    "y": ds["keys"],
                    "x": ds["values"],
                    "orientation": "h",
                    # "opacity": 0.5,
                }
            )
        else:
            chart_data.append(
                {
                    "type": "bar",
                    "name": ds["name"],
                    "x": ds["keys"],
                    "y": ds["values"],
                    # "opacity": 0.5,
                }
            )

    return compile_template_response(
        request,
        chart_data,
        input_data,
        options,
        {"barmode": barmode},
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
):
    # Parse URL params
    input_data = json.loads(unquote(data_json))

    # Compile Plotly data object
    chart_data = []
    for [_, ds] in enumerate(input_data):
        if horizontal:
            chart_data.append(
                {
                    "type": "scatter",
                    "mode": "lines",
                    "name": ds["name"],
                    "x": ds["y"],
                    "y": ds["x"],
                }
            )
        else:
            chart_data.append(
                {
                    "type": "scatter",
                    "mode": "lines",  # <--
                    "name": ds["name"],
                    "x": ds["x"],
                    "y": ds["y"],
                }
            )

    return compile_template_response(
        request,
        chart_data,
        input_data,
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
):

    # Parse URL params
    input_data = json.loads(unquote(data_json))

    # Compile Plotly data object
    chart_data = []
    for [_, ds] in enumerate(input_data):
        chart_data.append(
            {
                "type": "scatter",
                "mode": "markers",  # <--
                "name": ds["name"],
                "x": ds["x"],
                "y": ds["y"],
            }
        )

    return compile_template_response(
        request,
        chart_data,
        input_data,
        options,
    )


from enum import Enum


class ChartModes(Enum):
    LINE: str = "lines"
    PLOT: str = "markers"


# Bubble chart
# - - -
# https://plotly.com/javascript/bubble-charts/
@app.get("/chart/bubble", summary="Render a bubble chart from URL data")
async def chart_bubble(
    request: Request,
    data_json: str = Query(..., alias="data"),
    options: dict = Depends(chart_options),
):

    # Parse URL params
    input_data = json.loads(unquote(data_json))

    # Compile Plotly data object
    chart_data = []
    for [_, ds] in enumerate(input_data):
        chart_data.append(
            {
                "type": "scatter",
                "mode": "markers",  # <--
                "name": ds["name"],
                "x": ds["x"],
                "y": ds["y"],
                "marker": {"size": ds["size"]},
            }
        )

    return compile_template_response(
        request,
        chart_data,
        input_data,
        options,
    )


# Pie chart
# - - -
# https://plotly.com/javascript/pie-charts/
@app.get("/chart/pie", summary="Render a bubble chart from URL data")
async def chart_pie(
    request: Request,
    data_json: str = Query(..., alias="data"),
    options: dict = Depends(chart_options),
):

    # Parse URL params
    input_data = json.loads(unquote(data_json))

    # Compile Plotly data object
    chart_data = []
    for [_, ds] in enumerate(input_data):
        chart_data.append(
            {
                "type": "pie",
                "values": ds["values"],
                "labels": ds["labels"],
            }
        )

    return compile_template_response(
        request,
        chart_data,
        input_data,
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
):

    # Parse URL params
    input_data = json.loads(unquote(data_json))

    # Parse boxmean
    # Because it's a boolean OR a string, it's always parsed as a string
    # fmt: off
    boxmean = "sd" if boxmean is "sd" else True if boxmean in [True, "True", "true", "1"] else False
    # fmt: on

    # Determine box mode
    boxmode = "group" if "groups" in data_json else "overlay"

    # Compile Plotly data object
    chart_data = []
    for [_, ds] in enumerate(input_data):
        # fmt: off
        # ds["groups"]  = None
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

    return compile_template_response(
        request,
        chart_data,
        input_data,
        options,
        {"boxmode": boxmode},
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
):

    # Parse URL params
    input_data = json.loads(unquote(data_json))

    # Compile Plotly data object
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

    return compile_template_response(
        request,
        chart_data,
        input_data,
        options,
        {"barmode": barmode},
    )


# endregion

#
#
#
#
#


@app.get("/charts")
async def chart_files():
    """
    List all sample charts available in the sample-data directory.
    """

    sample_data_dir = "sample-data"
    files = os.listdir(sample_data_dir)
    links = [
        f"<a href='/chart/{file}'>{file}</a> - <a href='/sample-data/{file}?raw=1'>raw</a>"
        for file in files
        if file.endswith(".json")
    ]
    response_content = "<br>".join(links)
    return HTMLResponse(content=response_content, status_code=200)


@app.get("/chart_file/{filename}", summary="Render a chart from JSON data.")
async def chart_file(
    request: Request,
    filename: str,
    options: dict = Depends(chart_options),
):

    # Load json data from file
    with open(f"data_store/{filename}", encoding="utf-8") as f:
        chart_data = json.load(f)

    return compile_template_response(
        request,
        chart_data,
        options,
    )


#
#
#
#
#
#


@app.get(
    "/sample-data/{filename}",
    summary="Return sample chart data in JSON format.",
)
async def sample_data_file(filename: str, raw: Optional[bool] = Query(False)):
    """
    Return sample chart data in JSON format from a file in the sample-data directory.
    The filename should be a valid JSON file in the sample-data directory.
    """

    # Load json data from file
    with open(f"sample-data/{filename}", encoding="utf-8") as f:
        chart_data = json.load(f)

    # Convert the dictionary to a URL-encode JSON string
    json_string = json.dumps(chart_data, indent=2)
    encoded_data = quote(json_string)

    if raw:
        return PlainTextResponse(json_string)
    else:
        # return PlainTextResponse(f"http://localhost:8034/chart?data={encoded_data}")
        url = f"http://localhost:8034/chart?data={encoded_data}"
        return HTMLResponse(
            content=f"<a href='{url}' target='_blank'>View Chart</a>", status_code=200
        )


@app.get("/sample-data")
async def sample_data():
    """
    List all sample data files available in the sample-data directory.
    Returns links to JSON files that can be used with the /chart endpoint.
    """

    sample_data_dir = "sample-data"
    files = os.listdir(sample_data_dir)
    links = [
        f"<a href='/sample-data/{file}'>{file}</a> - <a href='/sample-data/{file}?raw=1'>raw</a>"
        for file in files
        if file.endswith(".json")
    ]
    response_content = "<br>".join(links)
    return HTMLResponse(content=response_content, status_code=200)


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


@app.get("/chart-v1", summary="Render a chart from JSON data.")
async def chart_v1(
    request: Request,
    data: str,
    width: int = 1000,
    height: int = 750,
    title: str = None,
    #
    # Interactive parameters
    subtitle: str = None,
    body: str = None,
):
    decoded_data = unquote(data)
    chart_data = json.loads(decoded_data)

    return templates.TemplateResponse(
        "chart-v1.jinja",
        {
            "request": request,
            "chart_data": chart_data,
            "palette": palette,
            "style": "B",
            # "opacity": 0.5,
            "width": width,
            "height": height,
            "title": title,
            "subtitle": subtitle,
            "body": body,
        },
    )


@app.get("/chart", summary="Render a chart from JSON data.")
async def chart(
    request: Request,
    data: str,
    width: int = 1000,
    height: int = 750,
    title: str = None,
    #
    # Interactive parameters
    subtitle: str = None,
    body: str = None,
):
    decoded_data = unquote(data)
    chart_data = json.loads(decoded_data)

    return templates.TemplateResponse(
        "chart.jinja",
        {
            "request": request,
            "chart_data": chart_data,
            "palette": palette,
            "style": "B",
            # "opacity": 0.5,
            "width": width,
            "height": height,
            "title": title,
            "subtitle": subtitle,
            "body": body,
        },
    )
