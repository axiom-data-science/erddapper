"""Delete all resources associated with a dataset and remove it from ERDDAP."""

import logging

from lxml.etree import fromstring

from erddapper.datasets.compose_datasets_xml import compose_datasets_xml
from erddapper.datasets.data_files import delete_data
from erddapper.datasets.reload_erddap import request_dataset_reload
from erddapper.store import delete_dataset_element, load_dataset_element


logger = logging.getLogger("erddapper")


async def delete_dataset(slug: str):
    """Delete all dataset resources and refresh ERDDAP."""
    delete_data(slug)
    # Read before deleting so we can get the ERDDAP dataset id
    xml_str = load_dataset_element(slug)
    if xml_str is None:
        return
    delete_dataset_element(slug)
    compose_datasets_xml()

    dataset = fromstring(xml_str)
    dataset_id = dataset.attrib.get("datasetID")
    if dataset_id is None:
        logger.error(
            f"Failed to get dataset ID from the dataset XML. Won't reload dataset {slug}."
        )
        return
    await request_dataset_reload(dataset_id)
