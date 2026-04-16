"""FastAPI application for erddapper."""

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI

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

app.include_router(main_router)
