"""Tests for dataset request union validation."""

import pytest

from pydantic import TypeAdapter, ValidationError

from erddapper.metadata.examples import (
    ASSET_MANAGER_REQUEST_EXAMPLE,
    INLINE_REQUEST_EXAMPLE,
    NCOJSON_INLINE_REQUEST_EXAMPLE,
)


@pytest.mark.parametrize(
    ("payload", "source_name"),
    [
        (INLINE_REQUEST_EXAMPLE, "inline"),
        (NCOJSON_INLINE_REQUEST_EXAMPLE, "ncojson-inline"),
        (ASSET_MANAGER_REQUEST_EXAMPLE, "asset-manager"),
    ],
)
def test_dataset_request_union_accepts_each_source(client, payload, source_name):
    from erddapper.metadata import CreateDatasetModelUnion

    request = TypeAdapter(CreateDatasetModelUnion).validate_python(payload)

    assert request.source_name == source_name


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"source_name": "unknown"},
        {"source_name": "inline"},
        {"source_name": "ncojson-inline", "file_type": "invalid"},
        {"source_name": "asset-manager", "acdd": "not-a-url"},
    ],
)
def test_dataset_request_union_rejects_invalid_requests(client, payload):
    from erddapper.metadata import CreateDatasetModelUnion

    with pytest.raises(ValidationError):
        TypeAdapter(CreateDatasetModelUnion).validate_python(payload)
