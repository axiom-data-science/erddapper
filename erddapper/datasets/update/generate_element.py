"""Generate ERDDAP dataset XML dataset elements."""

import logging

from typing import Iterable
from uuid import UUID

from lxml.etree import Element
from lxml.etree import tostring as xml_to_string

from erddapper.config import SETTINGS
from erddapper.utils.xml import (
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
    # String is the default
    "int": "int",
    "float": "double",
}


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
            "cell_header": f"={metadata['id']}",
            "cell_parameter": "station",
        }
    )
    variables.append(
        {
            "cell_header": "=0.0",
            "cell_parameter": "longitude",
        }
    )
    variables.append(
        {
            "cell_header": "=0.00",
            "cell_parameter": "latitude",
        }
    )

    for var in variables:
        if "cell_header" not in var:
            logger.warning(f"Ignoring an unidentified variable: {var}")
            continue
        var_elem = create_variable_subelement(
            dataset,
            var["cell_header"],
            var.get("cell_parameter", var["cell_header"]),
            "String"
            if var["cell_header"] == "dateTime"
            else "double",  # TODO: add this to the front end forms
        )
        var_attrs = create_subelement(var_elem, "addAttributes")
        add_attribute(var_attrs, "ioos_category", "Unknown")
        if var["cell_parameter"] == "station":
            add_attribute(var_attrs, "cf_role", "timeseries_id")
        if "time" in var["cell_header"].lower() or var["cell_header"] == "t":
            add_attribute(var_attrs, "units", "yyyy-MM-dd'T'HH:mm:ss'Z'")
            add_attribute(var_attrs, "time_format", "yyyy-MM-dd'T'HH:mm:ss'Z'")
            add_attribute(var_attrs, "standard_name", "time")
            add_attribute(var_attrs, "axis", "T")

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
