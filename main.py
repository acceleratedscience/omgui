from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from pydantic import BaseModel

# Tool
from render import render_molecule_svg_2d, render_molecule_svg_3d

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


class SmilesPayload(BaseModel):
    smiles: str


# Smiles as query parameter
@app.get("/render-molecule-svg", summary="SVG image of a small molecule")
def render_molecule_svg(
    smiles: str = Query(..., description="SMILES string of the molecule"),
    d3: bool = Query(False, description="Render in 3D if True, otherwise render in 2D"),
):
    """
    Render an SVG image of a small molecule from a SMILES string provided as query parameter.

    Example: http://localhost:8035/render-smol-svg?smiles=C1=CC=CC=C1
    """
    if d3:
        svg_str = render_molecule_svg_3d(smiles)
    else:
        svg_str = render_molecule_svg_2d(smiles)

    # Fail
    if svg_str is None:
        print("ERROR generating SVG for SMILES:", smiles)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid SMILES string, unable to generate SVG: {smiles}",
        )

    print("Success generating SVG for SMILES:", smiles)
    print("SVG:\n", svg_str)

    # Success
    return Response(
        content=svg_str,
        media_type="image/svg+xml",
        headers={"Content-Disposition": f'inline; filename="{smiles}.svg"'},
    )
