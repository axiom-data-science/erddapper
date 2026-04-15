"""Datasets router."""

from uuid import UUID

from fastapi import APIRouter, HTTPException

import erddapper.datasets as handlers

from erddapper.models import DatasetCreate
from erddapper.store import (
    dataset_element_exists,
    list_dataset_element_ids,
    load_dataset_element,
)


router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", response_model=list[UUID])
async def list_datasets() -> list[UUID]:
    """Return all datasets."""
    return list_dataset_element_ids()


@router.post("/{dataset_id}", status_code=201)
async def create_dataset(dataset_id: UUID, body: DatasetCreate):
    """Create a new dataset or update existing one using metadata from provided URLs."""
    await handlers.update_dataset(dataset_id, body)


@router.get("/{dataset_id}")
async def get_dataset(dataset_id: UUID) -> str:
    """Return a single dataset by ID."""
    dataset = load_dataset_element(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(dataset_id: UUID) -> None:
    """Delete a dataset and its XML dataset element."""
    if not dataset_element_exists(dataset_id):
        raise HTTPException(status_code=404, detail="Dataset not found")
    await handlers.delete_dataset(dataset_id)
