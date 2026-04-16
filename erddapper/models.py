"""Pydantic models for erddapper."""

from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class DatasetCreate(BaseModel):
    """Payload for creating or updating a dataset."""

    acdd_metadata: HttpUrl = Field(..., validation_alias="acdd")
    sample_file: HttpUrl

    model_config = {
        "extra": "ignore",
    }


class DatasetCreateResponse(BaseModel):
    """Response after creatin or update a dataset."""

    uuid: UUID
    erddap_dataset_id: str
