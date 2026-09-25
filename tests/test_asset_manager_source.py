"""Tests for Asset Manager dataset source."""

import httpx
import pytest

from pydantic import ValidationError

from erddapper.metadata.examples import ASSET_MANAGER_REQUEST_EXAMPLE
from erddapper.metadata.sources.asset_manager import AssetManagerParams


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
        ("not-json", 422),
        ({"id": "asset-manager-test"}, 422),
        ([], 422),
        (["not-an-object"], 422),
    ],
)
def test_asset_manager_rejects_invalid_metadata_response(
    client, monkeypatch, response_body, status_code
):
    patch_asset_manager_requests(monkeypatch, global_response=response_body)

    response = client.post(
        "/datasets/asset-manager-test",
        json=ASSET_MANAGER_REQUEST_EXAMPLE,
    )

    assert response.status_code == status_code


@pytest.mark.parametrize(
    ("upstream_status", "expected_status"),
    [(404, 422), (500, 502)],
)
def test_asset_manager_maps_response_http_status(
    client, monkeypatch, upstream_status, expected_status
):
    patch_asset_manager_requests(monkeypatch, global_status=upstream_status)

    response = client.post(
        "/datasets/asset-manager-test",
        json=ASSET_MANAGER_REQUEST_EXAMPLE,
    )

    assert response.status_code == expected_status


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
    assert response.json()["detail"] == "Linked metadata is invalid"


def test_asset_manager_returns_unprocessable_for_metadata_request_error(
    client, monkeypatch
):
    from erddapper.metadata.sources import asset_manager

    class FailingAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url):
            raise asset_manager.httpx.ConnectError(
                "connection failed",
                request=asset_manager.httpx.Request("GET", url),
            )

    monkeypatch.setattr(asset_manager.httpx, "AsyncClient", FailingAsyncClient)

    response = client.post(
        "/datasets/asset-manager-test",
        json=ASSET_MANAGER_REQUEST_EXAMPLE,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Failed to fetch linked metadata"


def patch_asset_manager_requests(monkeypatch, global_response=None, global_status=200):
    from erddapper.metadata.sources import asset_manager

    responses = {
        "https://metadata.example.com/global": global_response
        if global_response is not None
        else [
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
            status_code = global_status if str(url).endswith("/global") else 200
            return FakeResponse(url, responses[str(url)], status_code)

    class FakeResponse:
        def __init__(self, url, body, status_code):
            self.url = url
            self._body = body
            self.status_code = status_code

        def raise_for_status(self):
            if self.status_code < 400:
                return
            request = httpx.Request("GET", self.url)
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError(
                "upstream failure",
                request=request,
                response=response,
            )

        def json(self):
            if self._body == "not-json":
                raise ValueError("invalid JSON")
            return self._body

    monkeypatch.setattr(asset_manager.httpx, "AsyncClient", FakeAsyncClient)
