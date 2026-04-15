"""Delete all resources associated with a dataset and remove it from ERDDAP."""

from uuid import UUID

from erddapper.datasets.compose_datasets_xml import compose_datasets_xml
from erddapper.datasets.data_files import delete_data
from erddapper.datasets.reload_erddap import request_dataset_reload
from erddapper.store import delete_dataset_element


async def delete_dataset(uuid: UUID):
    """Delete all dataset resources and refresh ERDDAP."""
    delete_data(uuid)
    delete_dataset_element(uuid)
    compose_datasets_xml()
    await request_dataset_reload(uuid)
