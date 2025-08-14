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
# app.mount("/static", StaticFiles(directory="static"), name="static")


class SmilesPayload(BaseModel):
    smiles: str


# ------------------------------------
# Routes
# ------------------------------------


# Examples
@app.get("/", summary="Example links")
def examples():
    response = [
        "<a href='/demo'><button>Interactive demo</button></a>",
        "",
        "Example usage:<br>",
        "<a href='/Clc1cc(Cl)c(Cl)c(-c2c(Cl)c(Cl)cc(Cl)c2Cl)c1Cl'>2D example A</a>",
        "<a href='/CC(=O)OC1=CC=CC=C1C(=O)O'>2D example B (Aspirin)</a>",
        "<a href='/CN1C=NC2=C1C(=O)N(C(=O)N2C)C'>2D example C (Caffeine)</a>",
        "",
        "<a href='/Clc1cc(Cl)c(Cl)c(-c2c(Cl)c(Cl)cc(Cl)c2Cl)c1Cl?d3=1'>3D example A</a>",
        "<a href='/CC(=O)OC1=CC=CC=C1C(=O)O?d3=1'>3D example B (Aspirin)</a>",
        "<a href='/CN1C=NC2=C1C(=O)N(C(=O)N2C)C?d3=1'>3D example C (Caffeine)</a>",
    ]
    response_str = "<br>".join(response)
    return Response(content=response_str, media_type="text/html")


# Demo
@app.get(
    "/demo", response_class=HTMLResponse, summary="Interactive demo UI for the API"
)
def demo_page(request: Request):
    """
    Interactive HTML demo page for the Molecule Visualization API.
    Provides a user interface with controls for all API parameters.
    """
    return templates.TemplateResponse("demo.html", {"request": request})


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
    chart_data = {
        "labels": ["January", "February", "March", "April", "May", "June", "July"],
        "dataset1": {
            "label": "Dataset A",
            "data": [65, 59, 80, 81, 56, 55, 40],
            "backgroundColor": "red",
            "borderColor": "purple",
            "borderWidth": 2,
        },
        "dataset2": {
            "label": "Dataset B",
            "data": [28, 48, 40, 19, 86, 27, 90],
            "backgroundColor": "blue",
            "borderColor": "green",
            "borderWidth": 4,
        },
    }

    # Convert the dictionary to a JSON string
    json_string = json.dumps(chart_data)

    # URL-encode the JSON string
    encoded_data = quote(json_string)

    return PlainTextResponse(
        f"{json_string}\n\n---\n\nhttp://localhost:8034/chart?data={encoded_data}"
    )


@app.get("/chart/png", summary="Return a PNG image of a chart from JSON data.")
async def chart_png(data: str, width: int = 1000, height: int = 750):
    html_url = f"http://localhost:8034/chart?screenshot=true&width={width}&height={height}&data={data}"
    png_bytes = await screenshot(html_url)

    # # Disable caching
    # headers = {
    #     "Cache-Control": "no-cache, no-store, must-revalidate",
    #     "Pragma": "no-cache",
    #     "Expires": "0",
    # }

    return StreamingResponse(
        BytesIO(png_bytes),
        media_type="image/png",
        # headers=headers,
    )


@app.get("/chart", summary="Render a chart from JSON data.")
async def chart(
    request: Request,
    data: str,
    screenshot: bool = False,
    width: int = 1000,
    height: int = 750,
):
    decoded_data = unquote(data)
    chart_data = json.loads(decoded_data)
    return templates.TemplateResponse(
        "chart.jinja",
        {
            "request": request,
            "chart_data": chart_data,
            "screenshot": screenshot,
            "width": width,
            "height": height,
            "title": "Demo Chart",
            "subtitle": "Some subtitle",
            "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec tempor feugiat tortor eget pellentesque. Pellentesque quis luctus augue, eu pellentesque eros. Nullam ornare dictum odio, sit amet ullamcorper tellus tincidunt cursus. In molestie tempor augue nec elementum. Sed eu dolor quam. Sed sagittis vitae magna ullamcorper accumsan. Aenean eu tempor tellus. Donec ac consequat nisi. Aenean id lectus nibh.\n\nSed lobortis est purus, sed varius nunc viverra eget. Vivamus sit amet ligula tortor. Ut nibh sem, condimentum nec pulvinar in, suscipit vitae augue. Nam ac erat semper, semper nisi eget, consectetur nulla. Donec vitae risus et odio dignissim pharetra sit amet vitae mi. In varius dui odio, at commodo lorem aliquam eget. Vestibulum sed neque vel sem auctor feugiat eu vel arcu. Nulla facilisi. Etiam pharetra eros erat.",
        },
    )
