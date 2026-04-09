FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
LABEL org.opencontainers.image.authors="Honza Rychly <honza.rychly@tetratech.com>"

LABEL org.opencontainers.image.licenses="Apache-2.0"

ENV PROJECT_NAME=erddapper
ENV PROJECT_ROOT=/opt/erddapper

WORKDIR $PROJECT_ROOT/

COPY pyproject.toml README.md LICENSE conftest.py ./
COPY erddapper $PROJECT_ROOT/erddapper
COPY tests $PROJECT_ROOT/tests

RUN uv sync --no-dev
