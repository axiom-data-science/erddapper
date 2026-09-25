"""Tests for the FastAPI application."""

from erddapper.metadata.examples import (
    ASSET_MANAGER_REQUEST_EXAMPLE,
    INLINE_REQUEST_EXAMPLE,
    NCOJSON_INLINE_REQUEST_EXAMPLE,
)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_app_initializes(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "erddapper"


def test_openapi_includes_dataset_request_examples(client):
    schemas = client.get("/openapi.json").json()["components"]["schemas"]

    assert schemas["InlineParams"]["examples"] == [INLINE_REQUEST_EXAMPLE]
    assert schemas["NcoJsonInlineParams"]["examples"] == [NCOJSON_INLINE_REQUEST_EXAMPLE]
    assert schemas["AssetManagerParams"]["examples"] == [ASSET_MANAGER_REQUEST_EXAMPLE]
