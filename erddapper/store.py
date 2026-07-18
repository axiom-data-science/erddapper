"""Dataset element XML storage — pure functions; storage backend is opaque to callers."""

from pathlib import Path
from typing import Iterable

from erddapper.config import SETTINGS


def init_store():
    """Create dataset_elements_dir on app startup."""
    SETTINGS.dataset_elements_dir.mkdir(parents=True, exist_ok=True)


def get_dataset_element_path(slug: str) -> Path:
    """Return the filesystem path for the dataset element XML file."""
    return SETTINGS.dataset_elements_dir / f"{slug}.xml"


def dataset_element_exists(slug: str) -> bool:
    """Return True if a dataset element XML file exists for the given dataset."""
    return get_dataset_element_path(slug).exists()


def save_dataset_element(slug: str, xml: str) -> None:
    """Persist an XML dataset element for the given dataset."""
    dataset_element_path = get_dataset_element_path(slug)
    dataset_element_path.parent.mkdir(parents=True, exist_ok=True)
    dataset_element_path.write_text(xml, encoding="utf-8")


def load_dataset_element(slug: str) -> str | None:
    """Load the XML dataset element for the given dataset."""
    path = get_dataset_element_path(slug)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def delete_dataset_element(slug: str) -> None:
    """Delete the XML dataset element for the given dataset, ignoring missing files."""
    get_dataset_element_path(slug).unlink(missing_ok=True)


def list_dataset_element_ids() -> list[str]:
    """Return IDs of all stored dataset elements."""
    path = SETTINGS.dataset_elements_dir
    if not path.exists():
        raise NotADirectoryError(
            f"Configured XML dataset element directory '{path}' does not exist"
        )
    return [p.stem for p in path.glob("*.xml")]


def load_all_dataset_elements() -> Iterable[str]:
    """Return an iterator of all dataset element strings."""
    path = SETTINGS.dataset_elements_dir
    return (element_pth.read_text() for element_pth in path.glob("*.xml"))
