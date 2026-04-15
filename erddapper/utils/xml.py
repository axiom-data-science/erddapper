"""XML manipulation helpers."""

from typing import Optional

from lxml import etree


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
        element.text = _text
    return element


def add_attribute(
    parent: ElementT, name: str, value: Optional[str], type: Optional[str] = None
) -> ElementT:
    """Add an attribute to an element."""
    if type is not None:
        return create_subelement(parent, "att", value, name=name, type=type)
    return create_subelement(parent, "att", value, name=name)


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
    destination_name: str,
    data_type: str,
) -> ElementT:
    """Create a <dataVariable /> element with source and destination names."""
    data_variable = create_subelement(dataset, "dataVariable")
    create_subelement(data_variable, "sourceName", source_name)
    create_subelement(data_variable, "destinationName", destination_name)
    create_subelement(data_variable, "dataType", data_type)
    return data_variable
