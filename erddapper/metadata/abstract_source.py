"""Dataset source abstract class definition."""

from abc import ABC, abstractmethod
from typing import ClassVar, Generic, Type, TypeVar

from pydantic import BaseModel

from erddapper.models.metadata import AcddGlobalAttributes, SampleFileMetadata


class DatasetSourceRequestModel(BaseModel):
    """Placeholder request pseudo-model for static type checking.

    All implementations of DatasetSource must have a request model
    that includes a matching `source_name` discriminator.
    This is checked during the dynamic import.
    """

    source_name: str


RequestModel = TypeVar("RequestModel", bound=BaseModel)


class DatasetSource(ABC, Generic[RequestModel]):
    """Defines interface for obtaining data and metadata for a dataset."""

    SOURCE_NAME: ClassVar[str]
    REQUEST_MODEL: ClassVar[Type[BaseModel]]

    @staticmethod
    @abstractmethod
    async def get_metadata(
        body: RequestModel,
    ) -> tuple[AcddGlobalAttributes, SampleFileMetadata]:
        """Process request body and return necessary dataset metadata."""
        raise NotImplementedError
