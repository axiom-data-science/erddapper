"""Generate ERDDAP dataset XML dataset elements."""

import logging

from typing import Iterable
from uuid import UUID

from lxml.etree import Element
from lxml.etree import tostring as xml_to_string

from erddapper.config import SETTINGS
from erddapper.models.metadata import AcddGlobalAttributes, VariableMetadata
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
    "featureType": "timeSeries",
}

PYTHON_TYPE_MAPPING = {
    "str": "String",
    "int": "int",
    "float": "double",
}


def add_variable_xml(dataset_xml: ElementT, var: VariableMetadata):
    """Add variable element with its attributes."""

    var_xml = create_variable_subelement(
        dataset_xml,
        var.source_name,
        var.parameter_name,
        var.data_type,
    )

    var_attrs_xml = create_subelement(var_xml, "addAttributes")
    var_attrs = var.model_dump_var_attrs()
    # Fill in anything not present
    if "ioos_category" not in var_attrs:
        var_attrs["ioos_category"] = "Unknown"
    if var.parameter_name == "station" and "cf_role" not in var_attrs:
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
    uuid: UUID,
    global_attrs: AcddGlobalAttributes,
    variables: Iterable[VariableMetadata],
    dataset_id: str,
) -> str:
    """Build an ERDDAP dataset XML dataset element from metadata."""
    dataset = Element(
        "dataset",
        attrib={
            # Only worry about CSV file for now
            "type": "EDDTableFromAsciiFiles",
            "datasetID": dataset_id,
        },
    )
    create_subelement(
        dataset, "reloadEveryNMinutes", str(SETTINGS.dataset_reload_freq_min)
    )
    create_subelement(dataset, "fileDir", str(SETTINGS.erddap_datasets_path))
    create_subelement(dataset, "fileNameRegex", f"{uuid}.*")

    metadata = global_attrs.model_dump()
    # TODO: only add, don't overwrite
    metadata.update(ADDITIONAL_ATTRS)
    attrs = create_subelement(dataset, "addAttributes")
    for name, value in metadata.items():
        if value is None:
            continue
        mapped_type = PYTHON_TYPE_MAPPING.get(type(value).__name__)
        add_attribute(
            attrs,
            name,
            str(value),
            mapped_type or "String",
        )

    # FIXME: temporarily add computed variables
    variables = list(variables)
    variables.append(
        VariableMetadata(
            source_name=f'="{metadata["id"]}"',
            parameter_name="station",
            data_type="String",
        )
    )
    variables.append(
        VariableMetadata(
            source_name="=0.0",
            parameter_name="longitude",
            data_type="double",
        )
    )
    variables.append(
        VariableMetadata(
            source_name="=0.00",
            parameter_name="latitude",
            data_type="double",
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
