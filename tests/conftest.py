"""Shared pytest fixtures for API tests."""

import importlib

import pytest

from fastapi.testclient import TestClient


pytest_plugins = ("tests.fixtures.datasets",)


@pytest.fixture
def client(monkeypatch, tmp_path):
    """Return an isolated FastAPI test client with all sources enabled."""
    monkeypatch.setenv("ERDDAPPER_ERDDAP_BASE_URL", "http://example.com")
    monkeypatch.setenv("ERDDAPPER_ERDDAP_FLAG_KEY_KEY", "legit-flag-key-key-key-key")
    monkeypatch.setenv(
        "ERDDAPPER_ENABLED_SOURCES",
        "inline:InlineSource,inline:NcoJsonInlineSource,"
        "asset_manager:AssetManagerSource",
    )
    monkeypatch.setenv("ERDDAPPER_DATASET_ELEMENTS_DIR", str(tmp_path / "elements"))
    monkeypatch.setenv("ERDDAPPER_DATASET_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ERDDAPPER_DATASETS_XML_PATH", str(tmp_path / "datasets.xml"))

    import erddapper.config as config_module
    import erddapper.main as main_module
    import erddapper.metadata as metadata_module

    importlib.reload(config_module)
    importlib.reload(metadata_module)
    importlib.reload(main_module)

    with TestClient(main_module.app) as test_client:
        yield test_client
