"""Dataset metadata models."""

from typing import ClassVar, List, Literal, Optional

from pydantic import AnyUrl, BaseModel, Field, HttpUrl


# Only supporting time series for now
CdmDataType = Literal["TimeSeries"]
FeatureType = Literal["timeSeries"]


# TODO: we need to get latitude and longitude from somewhere
# (used to add computed lon/lat variables)


class AcddGlobalAttributes(BaseModel):
    """ACDD metadata for ERDDAP dataset's global attributes."""

    id: str
    # FIXME: temporarily add placeholder defaults for required stuff
    title: str = "PLACEHOLDER FOR DEMO"
    summary: str = "PLACEHOLDER FOR DEMO"
    institution: str = "PLACEHOLDER FOR DEMO"
    infoUrl: HttpUrl = HttpUrl("http://PLACEHOLDERFORDEMO.com")
    sourceUrl: HttpUrl = HttpUrl("http://PLACEHOLDERFORDEMO.com")
    cdm_data_type: CdmDataType = "TimeSeries"
    featureType: FeatureType = "timeSeries"
    cdm_timeseries_variables: str = "longitude,latitude,station"

    model_config = {
        "extra": "allow",  # allow other arbitrary attributes
    }


class VariableMetadata(BaseModel):
    """ACDD metadata and configuration for sample file variables."""

    source_name: str = Field(validation_alias="cell_header")
    parameter_name: str = Field(validation_alias="cell_parameter")
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

    NON_ATTR_FIELDS: ClassVar = ("source_name", "parameter_name", "data_type")

    def model_dump_var_attrs(self):
        """Return a dict with variable metadata attributes."""
        return {
            k: v
            for k, v in self.model_dump().items()
            if k not in self.NON_ATTR_FIELDS and v is not None
        }


class SampleFileMetadata(BaseModel):
    """Description of data file for use with ERDDAP."""

    variables: List[VariableMetadata] = Field(validation_alias="headers")
    file_uri: AnyUrl
