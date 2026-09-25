"""Tests for Asset Manager dataset source."""

import pytest

from fastapi import HTTPException
from pydantic import ValidationError

from erddapper.metadata.examples import ASSET_MANAGER_REQUEST_EXAMPLE
from erddapper.metadata.sources.asset_manager import (
    AssetManagerParams,
    parse_postgresty_response,
)


def test_create_dataset_from_asset_manager_payload(assert_dataset_creation, monkeypatch):
    patch_asset_manager_requests(monkeypatch)

    assert_dataset_creation(
        ASSET_MANAGER_REQUEST_EXAMPLE,
        "asset-manager-test",
        "asset-manager-test",
        "https://example.com/data/asset-manager-test.csv",
    )


def test_asset_manager_source_rejects_invalid_metadata_url():
    payload = {
        **ASSET_MANAGER_REQUEST_EXAMPLE,
        "acdd": "not-a-url",
    }

    with pytest.raises(ValidationError):
        AssetManagerParams.model_validate(payload)


@pytest.mark.parametrize(
    ("response_body", "status_code"),
    [
        ("not-json", 502),
        ({"id": "asset-manager-test"}, 400),
        ([], 404),
        (["not-an-object"], 400),
    ],
)
def test_asset_manager_rejects_invalid_metadata_response(response_body, status_code):
    response = FakeResponse("https://metadata.example.com/global", response_body)

    with pytest.raises(HTTPException) as error:
        parse_postgresty_response(response, "ACDD metadata")

    assert error.value.status_code == status_code


def test_asset_manager_rejects_malformed_metadata(client, monkeypatch):
    patch_asset_manager_requests(
        monkeypatch,
        global_response=[
            {
                "id": "asset-manager-test",
                "infoUrl": "not-a-url",
            }
        ],
    )

    response = client.post(
        "/datasets/asset-manager-test",
        json=ASSET_MANAGER_REQUEST_EXAMPLE,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Failed to retrieve linked metadata"


def patch_asset_manager_requests(monkeypatch, global_response=None):
    from erddapper.metadata.sources import asset_manager

    responses = {
        "https://metadata.example.com/global": global_response
        or [
            {
                "id": "asset-manager-test",
                "title": "Asset Manager test dataset",
                "summary": "Dataset created from Asset Manager metadata.",
                "institution": "Test institution",
                "infoUrl": "https://example.com/info",
                "sourceUrl": "https://example.com/source",
            }
        ],
        "https://metadata.example.com/file": [
            {
                "file_uri": "https://example.com/data/asset-manager-test.csv",
                "headers": [
                    {
                        "cell_header": "time",
                        "cell_units": "seconds since 1970-01-01T00:00:00Z",
                        "time_format": "yyyy-MM-dd'T'HH:mm:ss'Z'",
                        "data_type": "double",
                    }
                ],
            }
        ],
    }

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url):
            return FakeResponse(url, responses[str(url)])

    class FakeResponse:
        def __init__(self, url, body):
            self.url = url
            self._body = body

        def json(self):
            if self._body == "not-json":
                raise ValueError("invalid JSON")
            return self._body

    monkeypatch.setattr(asset_manager.httpx, "AsyncClient", FakeAsyncClient)


class FakeResponse:
    def __init__(self, url, body):
        self.url = url
        self._body = body

    def json(self):
        if self._body == "not-json":
            raise ValueError("invalid JSON")
        return self._body
