"""Application configuration via pydantic-settings."""

from pathlib import Path
from typing import Self

from pydantic import HttpUrl
from pydantic_core import core_schema
from pydantic_settings import BaseSettings, SettingsConfigDict


DUMMY_UUID = "fb40e19d-92d4-4995-b83c-854ccecfe40c"


class TemplateDatasetUrl(str):
    """A URL template string supporting {dataset_id} substitution.

    Validates that the value is a string with an http/https scheme.
    Use .format(dataset_id=id) to substitute the template variable into the URL.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, *_, **_kwargs):
        """Return the pydantic core schema for this type."""
        return core_schema.no_info_plain_validator_function(cls._validate)

    @classmethod
    def _validate(cls, value: object) -> Self:
        """Validate that value is a string with an http/https scheme."""
        if not isinstance(value, str):
            raise ValueError(f"TemplateDatasetUrl must be a string, got {type(value)}")
        # Try using the template and validate it as a URL
        HttpUrl(value.format(dataset_id=DUMMY_UUID))

        return cls(value)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ERDDAPPER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    dataset_elements_dir: Path = Path("datasets/elements")
    # The directory to which erddapper will save dataset data
    dataset_data_dir: Path = Path("datasets/data")
    datasets_xml_path: Path = Path("datasets/datasets.xml")
    # The path to datasets' data directory inside the ERDDAP container
    erddap_datasets_path: Path = Path("/mnt/datasets/data")
    erddap_base_url: HttpUrl
    erddap_flag_key_key: str
    dataset_reload_freq_min: int = 1440


SETTINGS = Settings()
