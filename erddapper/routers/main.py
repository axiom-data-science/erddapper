"""Main router composing all subrouters and simple endpoints."""

from fastapi import APIRouter

from erddapper.routers import datasets


router = APIRouter()

router.include_router(datasets.router)


@router.get("/health", tags=["health"])
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
