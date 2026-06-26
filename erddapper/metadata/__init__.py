"""Dynamically imported enabled Dataset Sources."""

from typing import TYPE_CHECKING

from erddapper.metadata.abstract_source import DatasetSourceRequestModel
from erddapper.metadata.import_sources import build_discriminated_union, import_sources


enabled_sources = import_sources()
discriminated_request_model_union = build_discriminated_union(
    s.REQUEST_MODEL for s in enabled_sources.values()
)
# A little hack to provide a valid type hint and also the pydantic models during runtime
if TYPE_CHECKING:
    CreateDatasetModelUnion = DatasetSourceRequestModel
else:
    CreateDatasetModelUnion = discriminated_request_model_union
