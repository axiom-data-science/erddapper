"""Datasets package."""

from erddapper.datasets.compose_datasets_xml import (
    compose_datasets_xml,
    init_datasets_xml_dir,
)
from erddapper.datasets.data_files import init_dataset_data_dir
from erddapper.datasets.delete import delete_dataset
from erddapper.datasets.reload_erddap import redact_flag_key
from erddapper.datasets.update import update_dataset


__all__ = [
    "compose_datasets_xml",
    "delete_dataset",
    "init_dataset_data_dir",
    "init_datasets_xml_dir",
    "redact_flag_key",
    "update_dataset",
]
