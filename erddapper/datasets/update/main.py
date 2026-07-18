"""Create or update dataset element."""

import logging
import re

from typing import Dict, Optional

from fastapi import HTTPException, status

from erddapper.datasets.compose_datasets_xml import compose_datasets_xml
from erddapper.datasets.data_files import download_data
from erddapper.datasets.reload_erddap import request_dataset_reload
from erddapper.datasets.update.generate_element import generate_dataset_xml
from erddapper.models.metadata import (
    DATASET_SLUG_REGEX,
    AcddGlobalAttributes,
    DataFileType,
    ErddapDatasetConfig,
    SampleFileMetadata,
    VariableMetadata,
)
from erddapper.store import save_dataset_element


logger = logging.getLogger("erddapper")


async def update_dataset(
    slug: str,
    file_type: DataFileType,
    global_attrs: AcddGlobalAttributes,
    variables: Dict[str, VariableMetadata],
    dataset_config: Optional[ErddapDatasetConfig],
    sample_file: Optional[SampleFileMetadata],
) -> str:
    """Create or update dataset element and return its ERDDAP dataset ID."""
    # datasetId for ERDDAP
    if not global_attrs.id:
        logger.error(f"Asset {slug} doesn't have global attribute 'id'.")
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Asset is missing global attribute 'id'",
        )

    if not re.fullmatch(DATASET_SLUG_REGEX, global_attrs.id):
        logger.error(
            f"Asset {slug} has attribute id {global_attrs.id} with invalid characters."
        )
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"id {global_attrs.id} has invalid chars, must match {DATASET_SLUG_REGEX}",
        )

    dataset_id = global_attrs.id

    # download data file if a url is provided
    # TODO should this be a separate method, or not supported at all?
    if sample_file and sample_file.file_uri:
        await download_data(slug, str(sample_file.file_uri))

    if not variables:
        logger.error(f"Asset {slug} doesn't have variable metadata.")
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Asset is missing variable metadata",
        )

    element = generate_dataset_xml(
        slug, dataset_id, file_type, dataset_config, global_attrs, variables.values()
    )
    save_dataset_element(slug, element)

    compose_datasets_xml()
    await request_dataset_reload(dataset_id)

    return dataset_id
