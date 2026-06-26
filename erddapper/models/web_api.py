"""Pydantic models for erddapper."""

from uuid import UUID

from pydantic import BaseModel


class DatasetCreateResponse(BaseModel):
    """Response after creating or updating a dataset."""

    uuid: UUID
    erddap_dataset_id: str
