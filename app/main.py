# Standard
from contextlib import asynccontextmanager

# Fast API
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, HTMLResponse

# Redis
import redis.asyncio as aioredis

# Routers
from .routers import charts, molecules


# Setup
# ------------------------------------


# Lifespan Event Handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifecycle of the application, including Redis connection.
    """

    # Logic to run on startup
    app.state.redis = aioredis.from_url(
        "redis://localhost:6379", encoding="utf-8", decode_responses=True
    )

    # The application will run from here
    yield

    # Logic to run on shutdown
    await app.state.redis.close()


# Initialize FastAPI
app = FastAPI(
    title="Data & molecule visualization API",
    version="1.0.0",
    description="Returns visualizations of data as Plotly charts in HTML, SVG or PNG format and molecules as 2D or 3D representations in SVG or PNG format.",
    lifespan=lifespan,
)

# Include routers
app.include_router(molecules.router, prefix="", tags=["molecules"])
app.include_router(charts.router, prefix="", tags=["charts"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up templates and static files
templates = Jinja2Templates(directory="app/templates")

# Mount static files directory if needed
app.mount("/static", StaticFiles(directory="app/static"), name="static")


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
