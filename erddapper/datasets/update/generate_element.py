"""Generate ERDDAP dataset XML dataset elements."""

import logging

from typing import Iterable
from uuid import UUID

from lxml.etree import Element
from lxml.etree import tostring as xml_to_string

from erddapper.config import SETTINGS
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
ALLOWED_VAR_ATTRS = [
    "time_format",
    "ioos_category",
    "cf_role",
    "units",
    "standard_name",
    "axis",
]

PYTHON_TYPE_MAPPING = {
    # String is the default
    "int": "int",
    "float": "double",
}


def add_variable_xml(dataset_xml: ElementT, var: dict):
    """Add variable element with its attributes."""
    if "cell_header" not in var:
        logger.warning(f"Ignoring an unidentified variable: {var}")
        return

    var_xml = create_variable_subelement(
        dataset_xml,
        var["cell_header"],
        var.get("cell_parameter", var["cell_header"]),
        "String"
        if var["cell_header"] == "dateTime"
        else "double",  # TODO: add this to the front end forms
    )

    var_attrs_xml = create_subelement(var_xml, "addAttributes")
    var_attrs = {k: v for k, v in var.items() if k in ALLOWED_VAR_ATTRS}
    # Fill in anything not present
    if "ioos_category" not in var_attrs:
        var_attrs["ioos_category"] = "Unknown"
    if var["cell_parameter"] == "station" and "cf_role" not in var_attrs:
        var_attrs["cf_role"] = "timeseries_id"
    if var.get("time_format"):
        if "units" not in var_attrs:
            var_attrs["units"] = var_attrs["time_format"]
        var_attrs["standard_name"] = "time"
        var_attrs["axis"] = "T"
    # Create the XML attributes
    for attr_name, attr_val in var_attrs.items():
        add_attribute(var_attrs_xml, attr_name, attr_val)


# TODO: add validation
# - ensure meta has REQUIRED_ATTRS
# TODO: estabilish a better source for these required attributes:
# - variables ioos_category, required variables: station, lon, lat
def generate_dataset_xml(
    uuid: UUID,
    metadata: dict,
    variables: Iterable[dict],
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

    # TODO: only add, don't overwrite
    metadata.update(ADDITIONAL_ATTRS)
    attrs = create_subelement(dataset, "addAttributes")
    for name, value in metadata.items():
        if value is None:
            continue
        add_attribute(
            attrs,
            name,
            value,
            PYTHON_TYPE_MAPPING.get(str(type(value)), "String"),
        )

    # FIXME: temporarily add computed variables
    variables = list(variables)
    variables.append(
        {
            "cell_header": f'="{metadata["id"]}"',
            "cell_parameter": "station",
            "data_type": "String",
        }
    )
    variables.append(
        {
            "cell_header": "=0.0",
            "cell_parameter": "longitude",
            "data_type": "double",
        }
    )
    variables.append(
        {
            "cell_header": "=0.00",
            "cell_parameter": "latitude",
            "data_type": "double",
        }
    )

    for var in variables:
        add_variable_xml(dataset, var)

    # FIXME: temporarily add placeholders so that all the required stuff present
    for name in REQUIRED_ATTRS:
        if metadata.get(name) is not None:
            continue
        add_attribute(attrs, name, "PLACEHOLDER FOR DEMO")

    return xml_to_string(
        dataset,
        encoding="unicode",
        pretty_print=True,
        xml_declaration=False,
    )
