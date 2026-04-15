"""Compose all dataset elements into a datasets.xml config."""

import logging

from erddapper.config import SETTINGS
from erddapper.store import load_all_dataset_elements


logger = logging.getLogger("erddapper")


DATASETS_TEMPLATE = """\
<?xml version="1.0" encoding="ISO-8859-1" ?>
<erddapDatasets>
    <requestBlacklist></requestBlacklist>

{elements}

</erddapDatasets>
"""


# TODO: this will probably require locks
def compose_datasets_xml():
    """Compose all dataset elements and write them into a datasets.xml config."""
    logger.debug("Refreshing datasets.xml")
    elements = "\n".join(load_all_dataset_elements())
    xml_bytes = DATASETS_TEMPLATE.format(elements=elements).encode("ISO-8859-1")
    SETTINGS.datasets_xml_path.write_bytes(xml_bytes)
