"""Application configuration via pydantic-settings."""

from pathlib import Path
from typing import Annotated, Optional, Self

from pydantic import HttpUrl, field_validator
from pydantic_core import core_schema
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


DUMMY_SLUG = "fb40e19d-92d4-4995-b83c-854ccecfe40c"


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
        HttpUrl(value.format(dataset_id=DUMMY_SLUG))

        return cls(value)


class Settings(BaseSettings):
    """Main pydantic config settings class."""

    model_config = SettingsConfigDict(
        env_prefix="ERDDAPPER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    dataset_elements_dir: Path = Path("datasets/elements")
    # The directory to which erddapper will save dataset data
    dataset_data_dir: Path | None = Path("datasets/data")
    datasets_xml_path: Path = Path("datasets/datasets.xml")
    # The path to datasets' data directory inside the ERDDAP container
    erddap_datasets_path: Path = Path("/mnt/datasets/data")
    erddap_base_url: HttpUrl
    erddap_flag_key_url: Optional[HttpUrl] = None
    erddap_flag_key_key: str
    erddap_reload_timeout: float = 30.0
    dataset_reload_freq_min: int = 1440

    enabled_sources: Annotated[list[str], NoDecode] = ["inline:InlineSource"]
    allowed_data_paths: Annotated[list[str], NoDecode] = ["/mnt/datasets/data", "/data"]

    @field_validator("enabled_sources", "allowed_data_paths", mode="before")
    @classmethod
    def parse_source_list(cls, v):
        """Parse input CSV string to list."""

        if not isinstance(v, str):
            return v
        return [s.strip() for s in v.split(",") if s.strip()]

    @field_validator("dataset_data_dir", mode="before")
    @classmethod
    def process_dataset_data_dir(cls, v):
        """Convert empty string to None for dataset_data_dir."""

        if not isinstance(v, str):
            return v

        if not v or not v.strip() or v.strip().lower() == "none":
            return None
        return v.strip() or None


SETTINGS = Settings()
