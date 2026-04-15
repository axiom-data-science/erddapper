"""Fetch dataset metadata from source URLs."""

import httpx

from fastapi import HTTPException, status
from pydantic import HttpUrl


def parse_postgresty_response(response: httpx.Response, descriptor: str) -> dict:
    """Parse a PostgREST JSON response, returning the first result object."""
    results = response.json()
    if not isinstance(results, list):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{descriptor} response body is not a json list",
        )
    if len(results) == 0:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"{descriptor} response contained empty list",
        )
    if not isinstance(results[0], dict):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{descriptor} response list does not contain a json object",
        )
    return results[0]


async def get_acdd_metadata(acdd_meta_url: HttpUrl) -> dict:
    """Fetch metadata from the configured source URL for dataset with uuid."""
    async with httpx.AsyncClient() as client:
        response = await client.get(str(acdd_meta_url))
    return parse_postgresty_response(response, "ACDD metadata")


async def get_sample_file_metadata(file_meta_url: HttpUrl) -> dict:
    """Fetch asset document metadata."""
    async with httpx.AsyncClient() as client:
        response = await client.get(str(file_meta_url))
    return parse_postgresty_response(response, "Asset document metadata")
