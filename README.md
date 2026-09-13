# erddapper

A dapper dataset manager for ERDDAP.

Currently, in a very prototypy state.

Copyright 2026 Axiom Data Science, LLC

See LICENSE for details.

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

1. Install uv by following the [official instructions](https://docs.astral.sh/uv/getting-started/installation/).

2. Clone this project with `git`.

3. Create the virtual environment and install dependencies:

    ```
    uv sync
    ```

4. To install dev dependencies (for testing and development):

    ```
    uv sync --group dev
    ```

## Running the Server

First, activate the virtual environment:

```
source .venv/bin/activate
```

Then start the server:

```
uvicorn erddapper.main:app --reload
```

API docs are available at <http://localhost:8000/docs> once the server is running.

## Running Tests

To run the project's tests:

```
uv run pytest -sv --integration
```

## Usage

The service is built using `fastapi` and exposes a `/docs` endpoint. You can find
a more complete list of available endpoint there.

Datasets get added and updated by a `POST` request at `/datasets/{slug}`.

### `asset-manager` source
For the `asset-manager` source type, the request payload is expected to contain an object
with URLs from which metadata and data for the dataset can be obtained.
It downloads the data to a configured directory, builds a `datasets.xml`,
and sends a dataset reload request to ERDDAP.

### `ncojson-inline` source

For the `ncojson-inline` source, the request payload should be an ncojson representation of the
dataset including global attributes and variables with attributes. Additionally, a top level
`"source_name": "ncojson-inline"` attribute should be specified. ERDDAP dataset config attributes
can optionally be included in a top level `config` object (example:
`"fileDir": "/data/some-operator/some-station").

See `./test-data/ncojson-inline/` for an example ncojson file.

## Configuration

Configuration is provided via environment variables (prefixed with `ERDDAPPER_`) or a `.env` file in the project root. Copy `.env.example` to `.env` and adjust as needed.

Dataset creation uses pluggable **dataset sources**. Each source defines how request
payload should be interpreted and where metadata comes from. Sources are implemented
in `erddapper.metadata.sources` and configured as `module_name:ClassName`.

| Variable | Required | Default | Description |
|---|---|---|---|
| `ERDDAPPER_ERDDAP_BASE_URL` | ✅ | — | Base URL of the ERDDAP instance *without `/erddap` path*, e.g. `http://localhost:8080`. |
| `ERDDAPPER_ERDDAP_FLAG_KEY_KEY` | ✅ | — | Key used to trigger ERDDAP flag reloads. |
| `ERDDAPPER_ERDDAP_FLAG_KEY_URL` | ❌ | — | Base ERDDAP URL to use specifically for flagKey generation (e.g. `https://localhost:8443`, the default `baseHttpsUrl` set in the ERDDAP Docker image. If not provided, `ERDDAPPER_ERDDAP_BASE_URL` is used, replacing `http://` with `https://`. |
| `ERDDAPPER_ENABLED_SOURCES` | ❌ | `inline:InlineSource` | Comma-separated list of enabled dataset source classes from `erddapper.metadata.sources` (format: `module:Class`). Example: `inline:InlineSource,asset_manager:AssetManagerSource`. |
| `ERDDAPPER_DATASET_ELEMENTS_DIR` | ❌ | `datasets/elements` | Directory where generated ERDDAP XML dataset elements are stored. |
| `ERDDAPPER_DATASET_DATA_DIR` | ❌ | `datasets/data` | Directory where downloaded dataset data files are stored. |
| `ERDDAPPER_DATASETS_XML_PATH` | ❌ | `datasets/datasets.xml` | Path to the generated `datasets.xml` config file. |
| `ERDDAPPER_ERDDAP_DATASETS_PATH` | ❌ | `/mnt/datasets/data` | Path to the datasets' data directory inside the ERDDAP container. |
| `ERDDAPPER_DATASET_RELOAD_FREQ_MIN` | ❌ | `1440` | How often ERDDAP should reload datasets, in minutes. |
| `ERDDAPPER_ALLOWED_DATA_PATHS` | ❌ | `/mnt/datasets/data,/data` | Which data root paths are allowed inside the ERDDAP container. |


## Building with Docker

To build the docker container:

```
docker build -t erddapper .
```

## Running with Docker

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.

## Technical TODOs
1. Correct async/blocking HTTP and add timeouts/status handling.
2. Make storage and datasets.xml writes atomic and concurrency-safe.
3. Add end-to-end tests around create/update/delete and both metadata sources.
4. Move settings/source initialization into controlled application startup.
5. Make SSRF protection and CORS configuration explicit before deployment.
