from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    Response,
    HTMLResponse,
    StreamingResponse,
    PlainTextResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Modules
import json
import logging
from io import BytesIO
from cairosvg import svg2png
from urllib.parse import quote, unquote
from pydantic import BaseModel
from typing import Optional, Literal

# Tool
from render import render_molecule_svg_2d, render_molecule_svg_3d, screenshot


# ------------------------------------
# Setup
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


# ------------------------------------
# Routes
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
        svg_str = render_molecule_svg_3d(
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
        svg_str = render_molecule_svg_2d(
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


@app.get("/sample_data")
async def sample_data():
    import random

    chart_data = {
        "labels": ["January", "February", "March"],
        "datasets": [],
    }

    for i in range(0, 16):
        chart_data["datasets"].append(
            {
                "label": f"Dataset {i}",
                "data": [random.randint(0, 100) for _ in range(0, 3)],
            }
        )

    # Convert the dictionary to a URL-encode JSON string
    json_string = json.dumps(chart_data)
    encoded_data = quote(json_string)

    return PlainTextResponse(
        f"{json_string}\n\n---\n\nhttp://localhost:8034/chart?data={encoded_data}"
    )


@app.get("/chart/png", summary="Return a PNG image of a chart from JSON data.")
async def chart_png(
    data: str,
    width: int = 1000,
    height: int = 750,
    title: str = None,
    #
    # PNG parameters
    scale: int = 1,
):
    data = quote(data)
    html_url = f"http://localhost:8034/chart?width={width}&height={height}&title={title}&data={data}"
    png_bytes = await screenshot(html_url, scale=scale)

    return StreamingResponse(
        BytesIO(png_bytes),
        media_type="image/png",
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
        # v3 - desat
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
        #
    ]
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
