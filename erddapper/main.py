"""FastAPI application for erddapper."""

from fastapi import FastAPI

from erddapper import __version__
from erddapper.routers import main_router


app = FastAPI(
    title="erddapper",
    description="A dapper dataset manager for ERDDAP.",
    version=__version__,
)

app.include_router(main_router)
