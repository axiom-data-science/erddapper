"""Setting ERDDAP reload flags."""

import hashlib
import logging
import re

import httpx

from fastapi import HTTPException, status
from pydantic import HttpUrl

from erddapper.config import SETTINGS


logger = logging.getLogger("erddapper")


def erddap_flag_key(
    erddap_base_url: HttpUrl,
    erddap_flag_key_url: HttpUrl,
    flag_key_key: str,
    dataset_id: str,
):
    """Compute the ERDDAP flag key hash for the given dataset."""
    # This needs to match how ERDDAP's base https url is configured
    # See https://github.com/ERDDAP/erddap/blob/main/WEB-INF/classes/gov/noaa/pfel/erddap/dataset/EDD.java#L3284 # noqa
    url = erddap_flag_key_url or str(erddap_base_url).replace("http://", "https://")
    phrase = f"{url}erddap_{dataset_id}_{flag_key_key}"
    return hashlib.sha256(str.encode(phrase)).hexdigest()


def redact_flag_key(msg: str) -> str:
    """Redact flagKey secret param from log messages."""

    if not msg:
        return msg

    return re.sub(r"flagKey=[0-9a-f]+", "flagKey=REDACTED", str(msg))


async def request_dataset_reload(dataset_id: str):
    """Request ERDDAP dataset reload by setting a flag file."""
    flag_key = erddap_flag_key(
        SETTINGS.erddap_base_url,
        SETTINGS.erddap_flag_key_url,
        SETTINGS.erddap_flag_key_key,
        dataset_id,
    )
    url = (
        f"{SETTINGS.erddap_base_url}erddap/setDatasetFlag.txt"
        f"?datasetID={dataset_id}&flagKey={flag_key}"
    )
    logger.debug(url)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=SETTINGS.erddap_reload_timeout)
        response.raise_for_status()
    except (httpx.RequestError, httpx.HTTPStatusError) as err:
        err_msg = (
            f"Failed to request reload for dataset '{dataset_id}': {redact_flag_key(err)}"
        )
        if isinstance(err, httpx.HTTPStatusError) and response.text:
            err_msg += f"\n{response.text}"

        logger.error(err_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err_msg
        )
