"""Datasets router."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

import erddapper.datasets as handlers

from erddapper.metadata import CreateDatasetModelUnion, enabled_sources
from erddapper.models import DATASET_SLUG_REGEX, DatasetCreateResponse
from erddapper.store import (
    dataset_element_exists,
    list_dataset_element_ids,
    load_dataset_element,
)


router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", response_model=list[str])
async def list_datasets() -> list[str]:
    """Return all datasets."""
    return list_dataset_element_ids()


@router.post("/{slug}", status_code=200)
async def create_dataset(
    slug: Annotated[str, Path(pattern=DATASET_SLUG_REGEX)], body: CreateDatasetModelUnion
) -> DatasetCreateResponse:
    """Create or update dataset using metadata from one of configured sources."""
    # Run-time pydantic model ensures source_name is an existing enabled one
    source = enabled_sources[body.source_name]
    (
        file_type,
        global_attrs,
        variables,
        dataset_config,
        sample_file,
    ) = await source.get_metadata(body)
    erddap_id = await handlers.update_dataset(
        slug, file_type, global_attrs, variables, dataset_config, sample_file
    )
    return DatasetCreateResponse(
        slug=slug,
        erddap_dataset_id=erddap_id,
    )


@router.get("/{slug}")
async def get_dataset(slug: Annotated[str, Path(pattern=DATASET_SLUG_REGEX)]) -> str:
    """Return a single dataset by ID."""
    dataset = load_dataset_element(slug)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.delete("/{slug}", status_code=204)
async def delete_dataset(slug: Annotated[str, Path(pattern=DATASET_SLUG_REGEX)]) -> None:
    """Delete a dataset and its XML dataset element."""
    if not dataset_element_exists(slug):
        raise HTTPException(status_code=404, detail="Dataset not found")
    await handlers.delete_dataset(slug)
