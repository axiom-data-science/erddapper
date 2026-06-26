"""Asset Manager dataset source implementation."""

from asyncio import gather
from typing import Literal

import httpx

from fastapi import HTTPException, status
from pydantic import BaseModel, Field, HttpUrl, ValidationError

from erddapper.metadata.abstract_source import DatasetSource
from erddapper.models.metadata import AcddGlobalAttributes, SampleFileMetadata


class AssetManagerParams(BaseModel):
    """Parameters to create dataset using Asset Manager as source."""

    source_name: Literal["asset-manager"]
    metadata_url: HttpUrl = Field(validation_alias="acdd")
    file_meta_url: HttpUrl = Field(validation_alias="sample_file")

    model_config = {"extra": "ignore"}


class AssetManagerSource(DatasetSource):
    """Asset Manager dataset source."""

    SOURCE_NAME = "asset-manager"
    REQUEST_MODEL = AssetManagerParams

    @staticmethod
    async def get_metadata(
        body: AssetManagerParams,
    ) -> tuple[AcddGlobalAttributes, SampleFileMetadata]:
        """Fetch asset document metadata from Asset Manager."""
        # TODO: only allow URLs pointing to whitelisted Asset Manager location
        async with httpx.AsyncClient() as client:
            gobal_meta_resp, file_meta_resp = await gather(
                client.get(str(body.metadata_url)),
                client.get(str(body.file_meta_url)),
            )
        try:
            global_meta = AcddGlobalAttributes(
                **{
                    k: v
                    for k, v in parse_postgresty_response(
                        gobal_meta_resp, "ACDD metadata"
                    ).items()
                    if v is not None
                }
            )
            file_meta = SampleFileMetadata(
                **parse_postgresty_response(file_meta_resp, "Asset document metadata")
            )
        except ValidationError as err:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(err))
        return global_meta, file_meta


def parse_postgresty_response(response: httpx.Response, descriptor: str) -> dict:
    """Parse a PostgREST JSON response, returning the first result object."""
    try:
        results = response.json()
    except Exception as err:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            f"Failed to fetch JSON from '{response.url}'",
        ) from err
    if not isinstance(results, list):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{descriptor} response body is not a json list",
        )
    if len(results) == 0:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"{descriptor} response contained empty list",
        )
    if not isinstance(results[0], dict):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{descriptor} response list does not contain a json object",
        )
    return results[0]
