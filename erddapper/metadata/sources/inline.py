"""Inline payload dataset source implementation."""

from typing import Annotated, Dict, List, Literal, Optional

from pydantic import BaseModel, BeforeValidator

from erddapper.metadata.abstract_source import DatasetSource
from erddapper.models.metadata import (
    AcddGlobalAttributes,
    DataFileType,
    ErddapDatasetConfig,
    SampleFileMetadata,
    VariableMetadata,
)


class InlineParams(BaseModel):
    """Parameters to create dataset using the inline metadata as source."""

    source_name: Literal["inline"]
    global_acdd: AcddGlobalAttributes
    variables: Dict[str, VariableMetadata]
    sample_file: SampleFileMetadata | None = None


class InlineSource(DatasetSource):
    """Inline payload dataset source."""

    SOURCE_NAME = "inline"
    REQUEST_MODEL = InlineParams

    @staticmethod
    async def get_metadata(
        body: InlineParams,
    ) -> tuple[
        DataFileType,
        AcddGlobalAttributes,
        Dict[str, VariableMetadata],
        Optional[ErddapDatasetConfig],
        Optional[SampleFileMetadata],
    ]:
        """Pass along dataset metadata from the request."""
        # FIXME hardcoding csv data file type for now
        return "csv", body.global_acdd, body.variables, None, body.sample_file


def convert_to_ncojson_level_1(attributes: dict) -> dict:
    """Convert verbose ncojson levels (>1) to concise level 1.

    Example: value {"type": "short", "data": [1, 2, 3]}
    would be converted to [1, 2, 3]
    """

    return {
        k: v
        if not isinstance(v, dict)
        else (
            v.get("data")
            if set(v.keys()) == {"data", "type"}
            else convert_to_ncojson_level_1(v)
        )
        for k, v in attributes.items()
    }


class NcoJsonVariable(BaseModel):
    """ncoJson variable object containing shape (optional), type, and attributes."""

    shape: Optional[List] = None
    type: str
    attributes: VariableMetadata


def set_variable_source_name_and_data_type(
    variables: Dict[str, NcoJsonVariable]
) -> Dict[str, NcoJsonVariable]:
    """Copy source_name and data_type into var attributes."""

    for var_name in variables:
        variable = variables[var_name]
        if "attributes" in variable:
            if "source_name" not in variable["attributes"]:
                variable["attributes"]["source_name"] = var_name
            if "data_type" not in variable["attributes"] and "type" in variable:
                variable["attributes"]["data_type"] = variable["type"]

    return variables


class NcoJsonInlineParams(BaseModel):
    """Dataset parameters using the inline ncoJson metadata."""

    source_name: Literal["ncojson-inline"]
    file_type: DataFileType
    config: Optional[ErddapDatasetConfig] = None
    attributes: Annotated[
        AcddGlobalAttributes, BeforeValidator(convert_to_ncojson_level_1)
    ]
    variables: Annotated[
        Dict[str, NcoJsonVariable],
        BeforeValidator(set_variable_source_name_and_data_type),
        BeforeValidator(convert_to_ncojson_level_1),
    ]


class NcoJsonInlineSource(DatasetSource):
    """Inline ncoJson style payload dataset source."""

    SOURCE_NAME = "ncojson-inline"
    REQUEST_MODEL = NcoJsonInlineParams

    @staticmethod
    async def get_metadata(
        body: NcoJsonInlineParams,
    ) -> tuple[
        DataFileType,
        AcddGlobalAttributes,
        Dict[str, VariableMetadata],
        Optional[ErddapDatasetConfig],
        Optional[SampleFileMetadata],
    ]:
        return (
            body.file_type,
            body.attributes,
            {k: v.attributes for k, v in body.variables.items()},
            body.config,
            None,
        )
