"""Inline payload dataset source implementation."""

from typing import Literal

from pydantic import BaseModel

from erddapper.metadata.abstract_source import DatasetSource
from erddapper.models.metadata import AcddGlobalAttributes, SampleFileMetadata


class InlineParams(BaseModel):
    """Parameters to create dataset using the inline metadata as source."""

    source_name: Literal["inline"]
    global_acdd: AcddGlobalAttributes
    file_meta: SampleFileMetadata


class InlineSource(DatasetSource):
    """Inline payload dataset source."""

    SOURCE_NAME = "inline"
    REQUEST_MODEL = InlineParams

    @staticmethod
    async def get_metadata(
        body: InlineParams,
    ) -> tuple[AcddGlobalAttributes, SampleFileMetadata]:
        """Pass along dataset metadata from the request."""
        return body.global_acdd, body.file_meta
