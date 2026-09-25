"""Example dataset source request payloads."""

INLINE_REQUEST_EXAMPLE = {
    "source_name": "inline",
    "global_acdd": {
        "id": "inline-test",
        "title": "Inline test dataset",
        "summary": "Dataset created from inline metadata.",
        "institution": "Test institution",
        "infoUrl": "https://example.com/info",
        "sourceUrl": "https://example.com/source",
    },
    "variables": {
        "time": {
            "source_name": "time",
            "data_type": "double",
            "units": "seconds since 1970-01-01T00:00:00Z",
            "time_format": "yyyy-MM-dd'T'HH:mm:ss'Z'",
        }
    },
    "sample_file_uri": "https://example.com/data/inline-test.csv",
}

NCOJSON_INLINE_REQUEST_EXAMPLE = {
    "source_name": "ncojson-inline",
    "file_type": "nc",
    "attributes": {
        "id": {"type": "char", "data": "ncojson-test"},
        "title": {"type": "char", "data": "NcoJSON test dataset"},
        "summary": {
            "type": "char",
            "data": "Dataset created from ncoJSON metadata.",
        },
        "institution": {"type": "char", "data": "Test institution"},
        "infoUrl": {"type": "char", "data": "https://example.com/info"},
        "sourceUrl": {"type": "char", "data": "https://example.com/source"},
    },
    "variables": {
        "time": {
            "type": "double",
            "attributes": {
                "units": "seconds since 1970-01-01T00:00:00Z",
                "time_format": "yyyy-MM-dd'T'HH:mm:ss'Z'",
            },
        }
    },
}

ASSET_MANAGER_REQUEST_EXAMPLE = {
    "source_name": "asset-manager",
    "acdd": "https://metadata.example.com/global",
    "sample_file": "https://metadata.example.com/file",
}
