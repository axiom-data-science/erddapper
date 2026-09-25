"""Shared pytest fixtures for API tests."""

import os

import pytest

from fastapi.testclient import TestClient


pytest_plugins = ("tests.fixtures.datasets",)

os.environ["ERDDAPPER_ERDDAP_BASE_URL"] = "http://example.com"
os.environ["ERDDAPPER_ERDDAP_FLAG_KEY_KEY"] = "legit-flag-key-key-key-key"
os.environ[
    "ERDDAPPER_ENABLED_SOURCES"
] = "inline:InlineSource,inline:NcoJsonInlineSource,asset_manager:AssetManagerSource"


@pytest.fixture
def test_settings(monkeypatch, tmp_path):
    """Return settings patched with isolated test paths."""
    import erddapper.config as config_module

    settings = config_module.SETTINGS
    monkeypatch.setattr(settings, "dataset_elements_dir", tmp_path / "elements")
    monkeypatch.setattr(settings, "dataset_data_dir", tmp_path / "data")
    monkeypatch.setattr(settings, "datasets_xml_path", tmp_path / "datasets.xml")
    return settings


@pytest.fixture
def client(test_settings):
    """Return an isolated FastAPI test client with all sources enabled."""
    import erddapper.main as main_module

    with TestClient(main_module.app) as test_client:
        yield test_client
