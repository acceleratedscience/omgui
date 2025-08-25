# Standard
import os
import logging
from dotenv import load_dotenv
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

# Load .env variables
load_dotenv()


# Logger
class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: "\x1b[90m",  # bright black / gray
        logging.INFO: "\x1b[32m",  # green
        logging.WARNING: "\x1b[33m",  # yellow
        logging.ERROR: "\x1b[31m",  # red
        logging.CRITICAL: "\x1b[1;31m",  # bold red
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, "\x1b[0m")
        # decorate the levelname only (keeps rest unchanged)
        record.levelname = f"{color}{record.levelname}\x1b[0m"
        return super().format(record)


# Configure root logger with a colored stream handler
root = logging.getLogger()
root.setLevel(logging.INFO)

# remove existing handlers if any (avoid duplicate logs)
if root.handlers:
    root.handlers.clear()

handler = logging.StreamHandler()
fmt = "\x1b[90m---------\x1b[0m %(levelname)s \x1b[90m%(name)s\x1b[0m %(message)s"
handler.setFormatter(ColoredFormatter(fmt))
root.addHandler(handler)
logger = logging.getLogger(__name__)


# Lifespan Event Handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifecycle of the application, including Redis connection.
    """

    # Read redis URL from environment; do not assume localhost in production
    redis_url = os.getenv("REDIS_URL")

    if redis_url:
        app.state.redis = aioredis.from_url(
            redis_url, encoding="utf-8", decode_responses=True
        )
        logger.info("✅ Connected to Redis")
    else:
        # No redis configured => set to None and use in-memory fallback where appropriate
        app.state.redis = None
        # simple in-memory cache for development/demo (not shared across processes)
        app.state.in_memory_cache = {}
        logger.info(
            "❌ Redis not available, defaulting to in-memory cache for demo purpose only"
        )

    # The application will run from here
    yield

    # Logic to run on shutdown
    if getattr(app.state, "redis", None):
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
