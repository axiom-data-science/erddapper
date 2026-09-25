"""Dataset creation test fixtures."""

import pytest


@pytest.fixture
def patch_dataset_side_effects(monkeypatch):
    """Patch dataset file download and ERDDAP reload side effects."""
    downloaded = []
    reloaded = []

    async def download_data(slug, file_uri):
        downloaded.append((slug, str(file_uri)))

    async def request_dataset_reload(dataset_id):
        reloaded.append(dataset_id)

    monkeypatch.setattr("erddapper.datasets.update.main.download_data", download_data)
    monkeypatch.setattr(
        "erddapper.datasets.update.main.request_dataset_reload",
        request_dataset_reload,
    )
    return downloaded, reloaded


@pytest.fixture
def assert_dataset_creation(client, patch_dataset_side_effects):
    """Return helper for asserting successful dataset creation."""

    def assert_created(payload, slug, dataset_id, download_uri=None):
        response = client.post(f"/datasets/{slug}", json=payload)

        assert response.status_code == 200
        assert response.json() == {
            "slug": slug,
            "erddap_dataset_id": dataset_id,
        }
        downloaded, reloaded = patch_dataset_side_effects
        expected_downloads = [(slug, download_uri)] if download_uri is not None else []
        assert downloaded == expected_downloads
        assert reloaded == [dataset_id]
        assert client.get(f"/datasets/{slug}").status_code == 200

    return assert_created
