"""Tests for inline dataset source."""

import pytest

from pydantic import ValidationError

from erddapper.metadata.examples import INLINE_REQUEST_EXAMPLE
from erddapper.metadata.sources.inline import InlineParams


def test_create_dataset_from_inline_payload(assert_dataset_creation):
    assert_dataset_creation(
        INLINE_REQUEST_EXAMPLE,
        "inline-test",
        "inline-test",
        "https://example.com/data/inline-test.csv",
    )


def test_inline_source_rejects_invalid_sample_file_uri():
    payload = {
        **INLINE_REQUEST_EXAMPLE,
        "sample_file_uri": "not-a-url",
    }

    with pytest.raises(ValidationError):
        InlineParams.model_validate(payload)
