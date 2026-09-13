"""erddapper Pydantic models."""

from erddapper.models.metadata import DATASET_SLUG_REGEX
from erddapper.models.web_api import DatasetCreateResponse


__all__ = [
    "DatasetCreateResponse",
    "DATASET_SLUG_REGEX",
]
