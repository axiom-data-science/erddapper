"""Dataset element XML storage — pure functions; storage backend is opaque to callers."""

from pathlib import Path
from typing import Iterable
from uuid import UUID

from erddapper.config import SETTINGS


def get_dataset_element_path(dataset_id: UUID) -> Path:
    """Return the filesystem path for the dataset element XML file."""
    return SETTINGS.dataset_elements_dir / f"{dataset_id}.xml"


def dataset_element_exists(dataset_id: UUID) -> bool:
    """Return True if a dataset element XML file exists for the given dataset."""
    return get_dataset_element_path(dataset_id).exists()


def save_dataset_element(dataset_id: UUID, xml: str) -> None:
    """Persist an XML dataset element for the given dataset."""
    get_dataset_element_path(dataset_id).write_text(xml, encoding="utf-8")


def load_dataset_element(dataset_id: UUID) -> str | None:
    """Load the XML dataset element for the given dataset."""
    path = get_dataset_element_path(dataset_id)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def delete_dataset_element(dataset_id: UUID) -> None:
    """Delete the XML dataset element for the given dataset, ignoring missing files."""
    get_dataset_element_path(dataset_id).unlink(missing_ok=True)


def list_dataset_element_ids() -> list[UUID]:
    """Return IDs of all stored dataset elements."""
    path = SETTINGS.dataset_elements_dir
    if not path.exists():
        raise NotADirectoryError(
            f"Configured XML dataset element directory '{path}' does not exist"
        )
    return [UUID(p.stem) for p in path.glob("*.xml")]


def load_all_dataset_elements() -> Iterable[str]:
    """Return an iterator of all dataset element strings."""
    path = SETTINGS.dataset_elements_dir
    return (element_pth.read_text() for element_pth in path.glob("*.xml"))
