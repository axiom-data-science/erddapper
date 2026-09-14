"""Dataset metadata models."""

from pathlib import Path
from typing import Any, ClassVar, Dict, List, Literal, Optional

from pydantic import AnyUrl, BaseModel, Field, HttpUrl, field_validator, model_validator

from erddapper.config import SETTINGS


# Only supporting time series for now
CdmDataType = Literal["TimeSeries"]
FeatureType = Literal["TimeSeries"]

# Supported data file types
DataFileType = Literal["csv", "nc"]

# Allowed characters for dataset slug
DATASET_SLUG_REGEX = r"^[A-Za-z0-9_-]+$"


# TODO: we need to get latitude and longitude from somewhere
# (used to add computed lon/lat variables)


class AcddGlobalAttributes(BaseModel):
    """ACDD metadata for ERDDAP dataset's global attributes."""

    id: str = Field(pattern=DATASET_SLUG_REGEX)
    # FIXME: temporarily add placeholder defaults for required stuff
    title: str = "PLACEHOLDER FOR DEMO"
    summary: str = "PLACEHOLDER FOR DEMO"
    institution: str = "PLACEHOLDER FOR DEMO"
    infoUrl: HttpUrl = HttpUrl("http://PLACEHOLDERFORDEMO.com")
    sourceUrl: HttpUrl = HttpUrl("http://PLACEHOLDERFORDEMO.com")
    cdm_data_type: CdmDataType = "TimeSeries"
    featureType: FeatureType = "TimeSeries"
    cdm_timeseries_variables: str = "longitude,latitude,station"

    model_config = {
        "extra": "allow",  # allow other arbitrary attributes
    }


class VariableMetadata(BaseModel):
    """ACDD metadata and configuration for sample file variables."""

    # TODO: asset manager should change to using standard
    #       source_name and destination_name parameters.
    #       once that happens we can remove these validation aliases
    source_name: str = Field(validation_alias="cell_header")
    destination_name: str | None = Field(default=None, validation_alias="cell_parameter")

    # We could also accept python or numpy types and map to java later
    data_type: Literal[
        "byte",
        "ubyte",
        "short",
        "ushort",
        "int",
        "uint",
        "long",
        "ulong",
        "float",
        "double",
        "char",
        "String",
    ] = "String"
    # Mandatory for some variables
    cf_role: Optional[str] = None
    # Mandatory for time variable
    units: Optional[str] = None
    time_format: Optional[str] = None
    standard_name: Optional[str] = None
    axis: Optional[str] = None

    model_config = {
        "extra": "allow",  # allow other arbitrary attributes
        "populate_by_name": True,  # allow either field name or its alias
    }

    NON_ATTR_FIELDS: ClassVar = ("source_name", "destination_name", "data_type")

    def model_dump_var_attrs(self):
        """Return a dict with variable metadata attributes."""
        return {
            k: v
            for k, v in self.model_dump().items()
            if k not in self.NON_ATTR_FIELDS and v is not None
        }


# TODO: This class is specific to asset-manager.
#       Should we move it to ./erddapper/metadata/sources/asset_manager.py?
class SampleFileMetadata(BaseModel):
    """Description of data file for use with ERDDAP."""

    file_uri: AnyUrl
    headers: List[Dict[str, Any]]
    variable_metadata: Dict[str, VariableMetadata]

    @model_validator(mode="before")
    @classmethod
    def parse_headers_to_variable_metadata(cls, data: Any) -> Any:
        """Parse asset_manager headers into Dict[str, VariableMetadata]."""

        if not isinstance(data, dict) or "headers" not in data:
            return data

        headers = data.get("headers")
        if not isinstance(headers, list):
            return data

        var_metas: Dict[str, VariableMetadata] = {}

        # map asset manager variable attributes to standard ncojson/ERDDAP names
        attr_map = {
            "cell_header": "source_name",
            "cell_parameter": "destination_name",
            "cell_units": "units",
        }
        for var in headers:
            var_meta = VariableMetadata.model_validate(
                {attr_map.get(k, k): v for k, v in var.items()}
            )
            var_metas[var_meta.source_name] = var_meta

        data["variable_metadata"] = var_metas
        return data


class ErddapDatasetConfig(BaseModel):
    """ERDDAP dataset configuration properties."""

    fileDir: Optional[str] = None

    @field_validator("fileDir")
    @classmethod
    def validate_fileDir(cls, value: str | None) -> str | None:
        """Ensure fileDir is within allowed root directories."""

        if value is None:
            return None

        path = Path(value).resolve()
        if not any(path.is_relative_to(p) for p in SETTINGS.allowed_data_paths):
            raise ValueError(
                f"fileDir must be in one of {SETTINGS.allowed_data_paths}, found {path}"
            )

        return str(path)

    model_config = {
        "extra": "allow",  # allow other arbitrary attributes
    }
