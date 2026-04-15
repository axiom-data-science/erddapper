"""Tests for the FastAPI application."""

import pytest

from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("ERDDAPPER_ERDDAP_BASE_URL", "http://example.com")
    monkeypatch.setenv("ERDDAPPER_ERDDAP_FLAG_KEY_KEY", "legit-flag-key-key-key-key")

    # Re-import app after env vars are set so Settings picks them up
    import importlib

    import erddapper.config as config_module
    import erddapper.main as main_module

    importlib.reload(config_module)
    importlib.reload(main_module)

    return TestClient(main_module.app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_app_initializes(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "erddapper"
