# Standard
import os

# import logging
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
import redis.exceptions

# Routers
from .routers import charts, molecules

from helpers import logger


# Setup
# ------------------------------------


# Load .env variables
load_dotenv()


# # -- Logger -- #


# # Logger: define format
# class ColoredFormatter(logging.Formatter):
#     LEVEL_COLORS = {
#         logging.DEBUG: "\x1b[90m",  # bright black / gray
#         logging.INFO: "\x1b[32m",  # green
#         logging.WARNING: "\x1b[33m",  # yellow
#         logging.ERROR: "\x1b[31m",  # red
#         logging.CRITICAL: "\x1b[1;31m",  # bold red
#         "RESET": "\x1b[0m",  # reset color
#     }

#     def format(self, record):
#         color_start = self.LEVEL_COLORS.get(record.levelno, self.LEVEL_COLORS["RESET"])
#         color_end = self.LEVEL_COLORS["RESET"]
#         log_message = super().format(record)
#         placeholder = f" {record.levelname} "
#         colored_levelname = f"{color_start}{record.levelname}{color_end}"
#         return log_message.replace(placeholder, f" {colored_levelname} ")


# # Logger: Configure
# root = logging.getLogger()
# root.setLevel(logging.INFO)

# # Logger: Avoid duplicate logs
# if root.handlers:
#     root.handlers.clear()

# # Logger: Initialize
# handler = logging.StreamHandler()
# fmt = "\x1b[90m---------\x1b[0m %(levelname)-8s \x1b[90m%(name)s\x1b[0m %(message)s"
# handler.setFormatter(ColoredFormatter(fmt))
# root.addHandler(handler)
# logger = logging.getLogger(__name__)


# -- FastAPI -- #


# Lifespan Event Handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifecycle of the application, including Redis connection.
    """
    redis_url = os.getenv("REDIS_URL")

    if redis_url:
        try:
            logger.info("REDIS_URL: %s", redis_url)
            app.state.redis = aioredis.from_url(
                redis_url, encoding="utf-8", decode_responses=True
            )
            await app.state.redis.ping()
            logger.info("📀 Redis connection successful")
        except redis.exceptions.ConnectionError:
            logger.error(
                "❌ Failed to connect to Redis --> Falling back to in-memory cache"
            )
            app.state.redis = None
            app.state.in_memory_cache = {}
    else:
        # No Redis URL provided, default to in-memory cache
        app.state.redis = None
        app.state.in_memory_cache = {}
        logger.info("REDIS_URL not available, defaulting to in-memory cache")

    # Application will run from here
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
app.include_router(molecules.router, prefix="/raw", tags=["Raw Molecules"])
app.include_router(charts.router, prefix="/raw", tags=["Raw Charts"])
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
