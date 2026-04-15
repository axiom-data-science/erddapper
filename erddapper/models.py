"""Pydantic models for erddapper."""

from pydantic import BaseModel, HttpUrl


class DatasetCreate(BaseModel):
    """Payload for creating a new dataset."""

    acdd_metadata: HttpUrl
    sample_file: HttpUrl

    model_config = {
        "extra": "ignore",
    }
