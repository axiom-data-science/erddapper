"""Tests for ncoJSON inline dataset source."""

import pytest

from pydantic import ValidationError

from erddapper.metadata.examples import NCOJSON_INLINE_REQUEST_EXAMPLE
from erddapper.metadata.sources.inline import NcoJsonInlineParams


def test_create_dataset_from_ncojson_inline_payload(
    assert_dataset_creation,
):
    assert_dataset_creation(
        NCOJSON_INLINE_REQUEST_EXAMPLE,
        "ncojson-test",
        "ncojson-test",
    )


def test_ncojson_inline_source_rejects_invalid_file_type():
    payload = {
        **NCOJSON_INLINE_REQUEST_EXAMPLE,
        "file_type": "json",
    }

    with pytest.raises(ValidationError):
        NcoJsonInlineParams.model_validate(payload)
