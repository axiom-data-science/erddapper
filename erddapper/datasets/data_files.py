"""Manage data files for datasets."""


from uuid import UUID

import httpx

from erddapper.config import SETTINGS


# MIME type to file extension map
CONTENT_TYPE_MAP = {
    "application/x-hdf5": "nc",
    "application/x-netcdf": "nc",
    "text/plain": "csv",  # *likely csv
}


async def download_data(uuid: UUID, file_uri: str):
    """Download dataset data to a file from configured URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(file_uri)
    extension = CONTENT_TYPE_MAP.get(response.headers.get("content-type", ""), "unknown")
    with open(SETTINGS.dataset_data_dir / f"{uuid}.{extension}", "wb") as file:
        file.write(response.content)


def delete_data(uuid: UUID):
    """Delete dataset data."""
    for data_file in SETTINGS.dataset_data_dir.glob(f"{uuid}.*"):
        data_file.unlink(missing_ok=True)
