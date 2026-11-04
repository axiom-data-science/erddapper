"""Tests for ncoJSON inline dataset source."""

import pytest

from pydantic import ValidationError

from erddapper.metadata.examples import (
    NCOJSON_INLINE_REQUEST_EXAMPLE,
    NCOJSON_INLINE_REQUEST_MINIMAL_ATTRS_EXAMPLE,
)
from erddapper.metadata.sources.inline import NcoJsonInlineParams
from erddapper.models.metadata import (
    PLACEHOLDER_INFO_URL,
    PLACEHOLDER_INSTITUTION,
    PLACEHOLDER_SOURCE_URL,
)


def test_create_dataset_from_ncojson_inline_payload(
    assert_dataset_creation,
):
    assert_dataset_creation(
        NCOJSON_INLINE_REQUEST_EXAMPLE,
        "ncojson-test",
        "ncojson-test",
        atts={
            "title": "NcoJSON test dataset",
            "summary": "Dataset created from ncoJSON metadata.",
            "institution": "Test institution",
            "infoUrl": "https://example.com/info",
            "sourceUrl": "https://example.com/source",
        },
    )


def test_ncojson_inline_source_rejects_invalid_file_type():
    payload = {
        **NCOJSON_INLINE_REQUEST_EXAMPLE,
        "file_type": "json",
    }

    with pytest.raises(ValidationError):
        NcoJsonInlineParams.model_validate(payload)


def test_create_dataset_from_ncojson_inline_minimal_payload(
    assert_dataset_creation,
):
    assert_dataset_creation(
        NCOJSON_INLINE_REQUEST_MINIMAL_ATTRS_EXAMPLE,
        "ncojson-minimal-test",
        "ncojson-minimal-test",
        atts={
            "title": "ncojson-minimal-test",
            "summary": "ncojson-minimal-test",
            "institution": PLACEHOLDER_INSTITUTION,
            "infoUrl": PLACEHOLDER_INFO_URL,
            "sourceUrl": PLACEHOLDER_SOURCE_URL,
        },
    )
