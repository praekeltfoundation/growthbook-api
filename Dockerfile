FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.7.5 /uv /usr/local/bin/uv
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    UV_PROJECT_ENVIRONMENT=/app
COPY . /src
WORKDIR /src
RUN uv sync \
    --locked \
    --no-dev \
    --no-editable

FROM python:3.12-slim
RUN useradd app
USER app
COPY --from=build --chown=app:app /app /app
WORKDIR /app
CMD ["bin/uvicorn", "growthbook_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
