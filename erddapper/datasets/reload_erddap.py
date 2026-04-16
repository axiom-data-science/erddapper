"""Setting ERDDAP reload flags."""

import hashlib
import logging

import httpx

from pydantic import HttpUrl

from erddapper.config import SETTINGS


logger = logging.getLogger("erddapper")


def erddap_flag_key(erddap_base_url: HttpUrl, flag_key_key: str, dataset_id: str):
    """Compute the ERDDAP flag key hash for the given dataset."""
    # This needs to match how ERDDAP's base https url is configured
    prefered_base_url = str(erddap_base_url).replace("http://", "https://")
    phrase = f"{prefered_base_url}erddap_{dataset_id}_{flag_key_key}"
    return hashlib.sha256(str.encode(phrase)).hexdigest()


async def request_dataset_reload(dataset_id: str):
    """Request ERDDAP dataset reload by setting a flag file."""
    flag_key = erddap_flag_key(
        SETTINGS.erddap_base_url, SETTINGS.erddap_flag_key_key, dataset_id
    )
    url = (
        f"{SETTINGS.erddap_base_url}erddap/setDatasetFlag.txt"
        f"?datasetID={dataset_id}&flagKey={flag_key}"
    )
    logger.debug(url)
    try:
        httpx.get(url)
    except httpx.ConnectError as err:
        logger.error(f"Failed to request reload for dataset '{dataset_id}': {err}")
