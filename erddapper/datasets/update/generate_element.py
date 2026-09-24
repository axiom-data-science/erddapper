"""Generate ERDDAP dataset XML dataset elements."""

import logging

from typing import Iterable, Optional

from lxml.etree import Element
from lxml.etree import tostring as xml_to_string

from erddapper.config import SETTINGS
from erddapper.models.metadata import (
    AcddGlobalAttributes,
    ErddapDatasetConfig,
    VariableMetadata,
)
from erddapper.utils.xml import (
    ElementT,
    add_attribute,
    create_subelement,
    create_variable_subelement,
)


logger = logging.getLogger("erddapper")


REQUIRED_ATTRS = [
    "id",
    "title",
    "summary",
    "institution",
    "infoUrl",
    "sourceUrl",
    "cdm_data_type",
    "cdm_timeseries_variables",
    "featureType",
]

ADDITIONAL_ATTRS = {
    "cdm_data_type": "TimeSeries",
    "cdm_timeseries_variables": "longitude,latitude,station",
    "featureType": "TimeSeries",
}

# https://erddap.github.io/docs/server-admin/datasets#eddtablefromfiles-skeleton-xml
ALLOWED_DATASET_CONFIG = [
    "reloadEveryNMinutes",
    "updateEveryNMillis",
    "standardizeWhat",
    "defaultDataQuery",
    "defaultGraphQuery",
    "addVariablesWhere",
    "nThreads",
    "fgdcFile",
    "iso19115File",
    "onChange",
    "fileDir",
    "recursive",
    "pathRegex",
    "fileNameRegex",
    "accessibleViaFiles",
    "metadataFrom",
    "charset",
    "skipHeaderToRegex",
    "skipLinesRegex",
    "columnNamesRow",
    "firstDataRow",
    "dimensionsCSV",
    "sortedColumnSourceName",
    "sortFilesBySourceNames",
    "sourceNeedsExpandedFP_EQ",
    "fileTableInMemory",
    "cacheFromUrl",
    "cacheSizeGB",
]

ERDDAP_DATASET_TYPES = {
    "csv": "EDDTableFromAsciiFiles",
    "nc": "EDDTableFromMultidimNcFiles",
}


def add_variable_xml(dataset_xml: ElementT, var: VariableMetadata):
    """Add variable element with its attributes."""

    var_xml = create_variable_subelement(
        dataset_xml,
        var.source_name,
        var.data_type,
        var.destination_name,
    )

    var_attrs_xml = create_subelement(var_xml, "addAttributes")
    var_attrs = var.model_dump_var_attrs()
    # Fill in anything not present
    if "ioos_category" not in var_attrs:
        var_attrs["ioos_category"] = "Unknown"
    if (
        var.destination_name or var.source_name
    ) == "station" and "cf_role" not in var_attrs:
        var_attrs["cf_role"] = "timeseries_id"
    if var_attrs.get("time_format"):
        if "units" not in var_attrs:
            var_attrs["units"] = var_attrs["time_format"]
        var_attrs["standard_name"] = "time"
        var_attrs["axis"] = "T"
    # Create the XML attributes
    for attr_name, attr_val in var_attrs.items():
        add_attribute(var_attrs_xml, attr_name, attr_val)


# TODO: estabilish a better source for these required attributes:
# - variables ioos_category, required variables: station, lon, lat
def generate_dataset_xml(
    slug: str,
    dataset_id: str,
    file_type: str,
    dataset_config: Optional[ErddapDatasetConfig],
    global_attrs: AcddGlobalAttributes,
    variables: Iterable[VariableMetadata],
) -> str:
    """Build an ERDDAP dataset XML dataset element from metadata."""

    if file_type not in ERDDAP_DATASET_TYPES:
        raise ValueError(
            f"Unsupported ERDDAP dataset file type {file_type}, "
            f"supported types are {', '.join(ERDDAP_DATASET_TYPES.keys())}"
        )

    dataset = Element(
        "dataset",
        attrib={
            "type": ERDDAP_DATASET_TYPES[file_type],
            "datasetID": dataset_id,
        },
    )

    # gather arbitraty erddap dataset config elements from request
    extra_dataset_configs = (
        dataset_config.model_extra
        if dataset_config and dataset_config.model_extra
        else {}
    )
    configs_batch = {
        **extra_dataset_configs,
        # Use specified fileDir config if provided or erddap_datasets_path root if not
        "fileDir": (
            dataset_config.fileDir
            if dataset_config and dataset_config.fileDir
            else str(SETTINGS.erddap_datasets_path / slug)
        ),
        # add reloadEveryNMinutes unless specified in dataset config
        "reloadEveryNMinutes": str(SETTINGS.dataset_reload_freq_min),
        # add fileNameRegex unless specified in dataset config
        "fileNameRegex": f".*\\.{file_type}",
        # add recursive unless specified in dataset config
        "recursive": "true",
    }
    for key, val in configs_batch:
        if key not in ALLOWED_DATASET_CONFIG:
            logger.warning(f"Dataset key {key} in {dataset_id} is not allowed, skipping")
            continue
        create_subelement(dataset, key, val)

    metadata = global_attrs.model_dump()
    # merge ADDITIONAL_ATTRS if they don't exist in metadata
    # TODO: all the ADDITIONAL_ATTRS defaults are already set
    # in the AcddGlobalAttributes model, so ADDITIONAL_ATTRS items
    # are currently never merged. Decide if we need ADDITIONAL_ATTRS.
    metadata = ADDITIONAL_ATTRS | metadata
    attrs = create_subelement(dataset, "addAttributes")
    for name, value in metadata.items():
        if value is None:
            continue

        add_attribute(attrs, name, value)

    variables = list(variables)
    var_names = [var.destination_name or var.source_name for var in variables]

    # FIXME: temporarily add computed variables if missing
    if "station" not in var_names:
        variables.append(
            VariableMetadata(
                source_name=f'="{metadata["id"]}"',
                data_type="String",
                destination_name="station",
            )
        )

    if "longitude" not in var_names:
        variables.append(
            VariableMetadata(
                source_name="=0.0",
                data_type="double",
                destination_name="longitude",
            )
        )

    if "latitude" not in var_names:
        variables.append(
            VariableMetadata(
                source_name="=0.00",
                data_type="double",
                destination_name="latitude",
            )
        )

    for var in variables:
        add_variable_xml(dataset, var)

    return xml_to_string(
        dataset,
        encoding="unicode",
        pretty_print=True,
        xml_declaration=False,
    )
