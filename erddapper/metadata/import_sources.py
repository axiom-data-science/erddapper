"""Metadata source extension loading logic."""

import logging

from functools import reduce
from importlib import import_module
from inspect import isabstract, isclass
from operator import or_
from typing import Annotated, Any, Iterable, Literal, cast

from pydantic import BaseModel, Field

from erddapper.config import SETTINGS
from erddapper.log import setup_logging
from erddapper.metadata.abstract_source import DatasetSource


# Call setup logging early here;
# needs to be called again in the fastapi life cycle function
setup_logging()
logger = logging.getLogger("erddapper")


def import_source(path: str) -> tuple[str, type[DatasetSource]]:
    """Import Dataset Source and return it."""
    logger.debug(f"Loading '{path}'.")
    try:
        module_name, class_name = path.split(":")
        module_path = f"erddapper.metadata.sources.{module_name}"
    except ValueError as err:
        raise ValueError(
            f"'{path}' must be in format 'MODULE_NAME:CLASS_NAME'", err
        ) from err
    try:
        module = import_module(module_path)
        source = getattr(module, class_name)
    except (ImportError, ModuleNotFoundError, AttributeError) as err:
        raise ValueError(
            f"Failed to import {class_name} from {module_name}", err
        ) from err

    # Validate the imported object
    if not isclass(source) or not issubclass(source, DatasetSource):
        raise TypeError(
            f"{source.__name__} must be a subclass of {DatasetSource.__name__}"
        )
    if isabstract(source):
        raise TypeError(
            f"{source.__name__} must implement {DatasetSource.__name__} completely"
        )

    source_name_field = source.REQUEST_MODEL.model_fields.get("source_name")
    if (
        source_name_field is None
        or source_name_field.annotation is None
        or source_name_field.annotation.__origin__ != Literal
        or source.SOURCE_NAME != source_name_field.annotation.__args__[0]
    ):
        raise TypeError(
            f"{source.__name__} must define a request model "
            f"with matching discriminator '{source.SOURCE_NAME}'"
        )

    return source.SOURCE_NAME, source


def import_sources() -> dict[str, type[DatasetSource]]:
    """Import all enabled Dataset Sources."""
    logger.debug("Loading dataset sources...")
    sources = dict(import_source(path) for path in SETTINGS.enabled_sources)
    logger.info(f"Loaded dataset sources: {', '.join(sources.keys())}.")
    return sources


def build_discriminated_union(models: Iterable[type[BaseModel]]):
    """Build a discriminated union out of Dataset Source request models."""
    union = reduce(or_, models)  # just like A | B | C...
    return Annotated[cast(Any, union), Field(discriminator="source_name")]
