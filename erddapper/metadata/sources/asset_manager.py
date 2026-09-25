"""Asset Manager dataset source implementation."""

from asyncio import gather
from typing import Dict, Literal, Optional

import httpx

from fastapi import HTTPException, status
from pydantic import AnyUrl, BaseModel, Field, HttpUrl, ValidationError, computed_field

from erddapper.metadata.abstract_source import DatasetSource
from erddapper.metadata.examples import ASSET_MANAGER_REQUEST_EXAMPLE
from erddapper.models.metadata import (
    AcddGlobalAttributes,
    DataFileType,
    ErddapDatasetConfig,
    VariableMetadata,
)


class AssetManagerParams(BaseModel):
    """Parameters to create dataset using Asset Manager as source."""

    source_name: Literal["asset-manager"]
    metadata_url: HttpUrl = Field(validation_alias="acdd")
    file_meta_url: HttpUrl = Field(validation_alias="sample_file")

    model_config = {
        "extra": "ignore",
        "json_schema_extra": {"examples": [ASSET_MANAGER_REQUEST_EXAMPLE]},
    }


class SampleFileMetadata(BaseModel):
    """Description of data file for use with ERDDAP."""

    file_uri: AnyUrl
    variables: list[VariableMetadata] = Field(validation_alias="headers")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def variable_metadata(self) -> Dict[str, VariableMetadata]:
        """Variable metadata by source name."""
        return {var.source_name: var for var in self.variables}


class AssetManagerSource(DatasetSource):
    """Asset Manager dataset source."""

    SOURCE_NAME = "asset-manager"
    REQUEST_MODEL = AssetManagerParams

    @staticmethod
    async def get_metadata(
        body: AssetManagerParams,
    ) -> tuple[
        DataFileType,
        AcddGlobalAttributes,
        Dict[str, VariableMetadata],
        Optional[ErddapDatasetConfig],
        Optional[AnyUrl],
    ]:
        """Fetch asset document metadata from Asset Manager."""
        # TODO: only allow URLs pointing to whitelisted Asset Manager location
        async with httpx.AsyncClient() as client:
            global_meta, file_meta = await gather(
                fetch_postgresty_response(
                    client, str(body.metadata_url), "ACDD metadata"
                ),
                fetch_postgresty_response(
                    client, str(body.file_meta_url), "Asset document metadata"
                ),
            )
        try:
            global_meta = AcddGlobalAttributes(
                **{k: v for k, v in global_meta.items() if v is not None}
            )
            file_meta = SampleFileMetadata(**file_meta)
        except ValidationError as err:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                "Linked metadata is invalid",
            ) from err

        # FIXME hardcoding csv as filetype for now
        return "csv", global_meta, file_meta.variable_metadata, None, file_meta.file_uri


async def fetch_postgresty_response(
    client: httpx.AsyncClient, url: str, descriptor: str
) -> dict:
    """Fetch and parse the first object from a PostgREST JSON response."""

    # Retrieve response and handle errors
    try:
        response = await client.get(url)
        response.raise_for_status()
    except httpx.RequestError as err:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Failed to fetch linked metadata",
        ) from err
    except httpx.HTTPStatusError as err:
        error_status = (
            status.HTTP_502_BAD_GATEWAY
            if err.response.status_code >= 500
            else status.HTTP_422_UNPROCESSABLE_CONTENT
        )
        raise HTTPException(
            error_status,
            "Failed to fetch linked metadata",
        ) from err

    # Parse successful response body
    try:
        results = response.json()
    except ValueError as err:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"Failed to fetch JSON from '{response.url}'",
        ) from err
    if not isinstance(results, list):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"{descriptor} response body is not a json list",
        )
    if len(results) == 0:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"{descriptor} response contained empty list",
        )
    if not isinstance(results[0], dict):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"{descriptor} response list does not contain a json object",
        )

    return results[0]
