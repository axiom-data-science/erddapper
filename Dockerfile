FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
LABEL org.opencontainers.image.authors="Honza Rychly <honza.rychly@tetratech.com>"

LABEL org.opencontainers.image.licenses="Apache-2.0"

ENV PROJECT_NAME=erddapper
ENV PROJECT_ROOT=/opt/erddapper

WORKDIR $PROJECT_ROOT/

# Install dependencies first for better layer caching
COPY pyproject.toml uv.lock README.md LICENSE ./
RUN uv sync --no-dev --frozen --no-install-project

# Copy source and install the project
COPY erddapper $PROJECT_ROOT/erddapper
RUN uv sync --no-dev --frozen

ENV PATH="$PROJECT_ROOT/.venv/bin:$PATH"

CMD ["uvicorn", "erddapper.main:app", "--host", "0.0.0.0", "--port", "8080"]
