from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Modules
import base64
import logging
from io import BytesIO
from cairosvg import svg2png
from pydantic import BaseModel
from typing import Optional, Literal

# Tool
from render import render_molecule_svg_2d, render_molecule_svg_3d


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


# fmt:off
# Smiles as query parameter
@app.get("/{smiles}", summary="Visualize any molecule from a SMILES string")
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

    # fmt:on

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
