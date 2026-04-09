# erddapper

A dapper dataset manager for ERDDAP.

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

## Configuration

## Building with Docker

To build the docker container:

```
docker build -t erddapper .
```

## Running with Docker

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
