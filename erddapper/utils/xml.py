"""XML manipulation helpers."""

import logging

from typing import Any, Optional

from lxml import etree


logger = logging.getLogger("erddapper")


# https://erddap.github.io/docs/server-admin/datasets#attributetype
PYTHON_TO_ERDDAP_TYPE_MAPPING = {
    "str": "String",
    "int": "int",
    "float": "double",
    "list[int]": "intList",
    "list[float]": "doubleList",
    "HttpUrl": "String",
}


# Represents an XML Element.
ElementT = etree._Element


def create_subelement(
    _parent: ElementT,
    _tag: str,
    _text: Optional[str] = None,
    attrib: Optional[dict] = None,
    nsmap: Optional[dict] = None,
    **_extra,
) -> ElementT:
    """Create a subelement with text."""
    element = etree.SubElement(_parent, _tag, attrib=attrib, nsmap=nsmap, **_extra)
    if _text is not None:
        element.text = str(_text)
    return element


def add_attribute(parent: ElementT, name: str, value: Any) -> ElementT | None:
    """Add an attribute to an element."""

    is_list = isinstance(value, list)

    if is_list:
        if len(value) == 0:
            # empty list, no need to add attr
            return None
        python_type = f"list[{type(value[0]).__name__}]"
    else:
        python_type = type(value).__name__

    erddap_type = PYTHON_TO_ERDDAP_TYPE_MAPPING.get(python_type)
    if not erddap_type:
        logger.warn(f"{name} has unhandled python type {python_type}, using String")
        erddap_type = "String"

    if erddap_type == "String":
        # create without specifying a type, String is the default for ERDDAP atts
        return create_subelement(parent, "att", value, name=name)

    if is_list and erddap_type.endswith("List"):
        # format to space separated ERDDAP att value format
        value = " ".join((str(v) for v in value))

    return create_subelement(parent, "att", value, name=name, type=erddap_type)


def delete_element(el: ElementT) -> bool:
    """Remove an element from its parent."""
    parent = el.getparent()
    if parent is None:
        return False
    parent.remove(el)
    return True


def create_variable_subelement(
    dataset: ElementT,
    source_name: str,
    data_type: str,
    destination_name: Optional[str] = None,
) -> ElementT:
    """Create a <dataVariable /> element with source and destination names."""
    data_variable = create_subelement(dataset, "dataVariable")
    create_subelement(data_variable, "sourceName", source_name)
    create_subelement(data_variable, "destinationName", destination_name or source_name)
    create_subelement(data_variable, "dataType", data_type)
    return data_variable
