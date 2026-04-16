"""Create or update dataset element."""

import logging

from uuid import UUID

from fastapi import HTTPException, status

from erddapper.datasets.compose_datasets_xml import compose_datasets_xml
from erddapper.datasets.data_files import download_data
from erddapper.datasets.reload_erddap import request_dataset_reload
from erddapper.datasets.update.generate_element import generate_dataset_xml
from erddapper.datasets.update.metadata import get_acdd_metadata, get_sample_file_metadata
from erddapper.models import DatasetCreate
from erddapper.store import save_dataset_element


logger = logging.getLogger("erddapper")


async def update_dataset(uuid: UUID, request: DatasetCreate) -> str:
    """Create or update dataset element and return its ERDDAP dataset ID."""
    acdd_meta = await get_acdd_metadata(request.acdd_metadata)

    assert "id" in acdd_meta, "Asset metadata must contain 'id'"
    # datasetId for ERDDAP
    dataset_id = acdd_meta["id"]

    sample_file = await get_sample_file_metadata(request.sample_file)
    file_uri = sample_file.get("file_uri")
    if file_uri:
        await download_data(uuid, file_uri)
    else:
        logger.error(f"Asset doc {uuid} has no sample file URI: {sample_file}")
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Asset document is missing sample file URI"
        )
    if not sample_file.get("headers"):
        logger.error(f"Asset doc {uuid} doesn't have file header metadata.")
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Asset document is missing sample file headers",
        )

    element = generate_dataset_xml(uuid, acdd_meta, sample_file["headers"], dataset_id)
    save_dataset_element(uuid, element)

    compose_datasets_xml()
    await request_dataset_reload(dataset_id)

    return dataset_id
