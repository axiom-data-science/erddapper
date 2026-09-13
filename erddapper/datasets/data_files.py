"""Manage data files for datasets."""


import httpx

from erddapper.config import SETTINGS


# MIME type to file extension map
CONTENT_TYPE_MAP = {
    "application/x-hdf5": "nc",
    "application/x-netcdf": "nc",
    "text/plain": "csv",  # *likely csv
    "text/csv": "csv",  # *definitely csv
}


def init_dataset_data_dir():
    """Create dataset_data_dir on app startup."""
    if SETTINGS.dataset_data_dir:
        SETTINGS.dataset_data_dir.mkdir(parents=True, exist_ok=True)


async def download_data(slug: str, file_uri: str):
    """Download dataset data to a file from configured URL."""

    if not SETTINGS.dataset_data_dir:
        raise NotImplementedError("Data downloads are disabled")

    async with httpx.AsyncClient() as client:
        response = await client.get(file_uri)
    response.raise_for_status()

    content_type = response.headers.get("content-type", "").split(";")[0].strip()
    if content_type not in CONTENT_TYPE_MAP:
        raise ValueError(f"Unsupported Content-Type {content_type}")
    extension = CONTENT_TYPE_MAP.get(content_type)

    (SETTINGS.dataset_data_dir / slug).mkdir(parents=True, exist_ok=True)
    with open(SETTINGS.dataset_data_dir / slug / f"{slug}.{extension}", "wb") as file:
        file.write(response.content)


def delete_data(slug: str):
    """Delete dataset data."""

    if not SETTINGS.dataset_data_dir:
        return

    dataset_dir = SETTINGS.dataset_data_dir / slug
    if dataset_dir.is_dir():
        for data_file in dataset_dir.iterdir():
            if data_file.is_file():
                data_file.unlink(missing_ok=True)
        dataset_dir.rmdir()
