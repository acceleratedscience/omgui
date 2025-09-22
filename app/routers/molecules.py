"""
Molecule-related API routes.
"""

# Standard
import logging
from io import BytesIO
from typing import Literal

# Fast API
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException, Query
from fastapi.responses import Response
from fastapi import APIRouter

# Modules
from cairosvg import svg2png

# Tools
from ..workers import svgmol_2d, svgmol_3d


# Setup
# ------------------------------------

# Router
router = APIRouter()

# Set up templates and static files
templates = Jinja2Templates(directory="app/templates")

logger = logging.getLogger(__name__)


# Routes
# ------------------------------------


# Smiles as query parameter
@router.get("/molecule/{smiles}", summary="Visualize any molecule from a SMILES string")
def visualize_molecule(
    # fmt: off
    # Input
    smiles: str,

    # Options
    png: bool = Query(False, description="Render as PNG if True, otherwise render as SVG"),
    width: int = Query(800, description="Width of the rendered image in pixels"),
    height: int = Query(600, description="Height of the rendered image in pixels"),
    highlight: str = Query(None, description="SMARTS substructure to highlight in the molecule"),
    d3: bool = Query(False, description="Render in 3D if True, otherwise render in 2D"),

    # 3D options
    d3_style: Literal["SPACEFILLING", "BALL_AND_STICK", "TUBE", "WIREFRAME"] = Query("BALL_AND_STICK", description="3D rendering style"),
    d3_look: Literal["CARTOON", "GLOSSY"] = Query("CARTOON", description="3D rendering look"),
    d3_rot_x: float | None = Query(None, description="Rotation around x-axis in units of 60 degrees"),
    d3_rot_y: float | None = Query(None, description="Rotation around y-axis in units of 60 degrees"),
    d3_rot_z: float | None = Query(None, description="Rotation around z-axis in units of 60 degrees"),
    d3_rot_random: bool = Query(True, description="Random rotation per axis if no rotation angles are provided"),
    # fmt: on
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
        logger.info("ERROR generating SVG for SMILES: %s", smiles)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid SMILES string, unable to generate SVG: {smiles}",
        )

    # Success
    logger.info("Success generating SVG for SMILES: %s", smiles)
    logger.info("\nSVG:\n---\n%s", svg_str)

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
