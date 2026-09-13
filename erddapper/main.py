"""FastAPI application for erddapper."""

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from erddapper import __version__
from erddapper.datasets import (
    compose_datasets_xml,
    init_dataset_data_dir,
    init_datasets_xml_dir,
)
from erddapper.log import setup_logging
from erddapper.routers import main_router
from erddapper.store import init_store


logger = logging.getLogger("erddapper")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Service lifespan context manager."""
    setup_logging()
    logger.debug("Logging configured")
    init_store()
    compose_datasets_xml()
    init_datasets_xml_dir()
    init_dataset_data_dir()
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
