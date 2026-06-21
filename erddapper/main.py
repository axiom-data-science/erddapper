"""FastAPI application for erddapper."""

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from erddapper import __version__
from erddapper.log import setup_logging
from erddapper.routers import main_router


logger = logging.getLogger("erddapper")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Service lifespan context manager."""
    setup_logging()
    logger.debug("Logging configured")
    yield


app = FastAPI(
    title="erddapper",
    description="A dapper dataset manager for ERDDAP.",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)
