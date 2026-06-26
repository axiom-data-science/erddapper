"""Create or update dataset element."""

import logging

from uuid import UUID

from fastapi import HTTPException, status

from erddapper.datasets.compose_datasets_xml import compose_datasets_xml
from erddapper.datasets.data_files import download_data
from erddapper.datasets.reload_erddap import request_dataset_reload
from erddapper.datasets.update.generate_element import generate_dataset_xml
from erddapper.models.metadata import AcddGlobalAttributes, SampleFileMetadata
from erddapper.store import save_dataset_element


logger = logging.getLogger("erddapper")


async def update_dataset(
    uuid: UUID,
    global_attrs: AcddGlobalAttributes,
    sample_file: SampleFileMetadata,
) -> str:
    """Create or update dataset element and return its ERDDAP dataset ID."""
    # datasetId for ERDDAP
    dataset_id = global_attrs.id
    if sample_file.file_uri:
        await download_data(uuid, str(sample_file.file_uri))
    else:
        logger.error(f"Asset doc {uuid} has no sample file URI: {sample_file}")
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Asset document is missing sample file URI"
        )
    if not sample_file.variables:
        logger.error(f"Asset doc {uuid} doesn't have file header metadata.")
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Asset document is missing sample file headers",
        )

    element = generate_dataset_xml(uuid, global_attrs, sample_file.variables, dataset_id)
    save_dataset_element(uuid, element)

    compose_datasets_xml()
    await request_dataset_reload(dataset_id)

    return dataset_id
