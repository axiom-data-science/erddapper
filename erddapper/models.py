"""Pydantic models for erddapper."""

from pydantic import BaseModel, Field, HttpUrl


class DatasetCreate(BaseModel):
    """Payload for creating a new dataset."""

    acdd_metadata: HttpUrl = Field(..., validation_alias="acdd")
    sample_file: HttpUrl

    model_config = {
        "extra": "ignore",
    }
