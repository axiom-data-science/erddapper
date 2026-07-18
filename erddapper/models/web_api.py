"""Pydantic models for erddapper."""

from pydantic import BaseModel


class DatasetCreateResponse(BaseModel):
    """Response after creating or updating a dataset."""

    slug: str
    erddap_dataset_id: str
