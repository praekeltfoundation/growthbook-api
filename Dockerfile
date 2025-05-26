FROM python:3.12-slim as build
COPY --from=ghcr.io/astral-sh/uv:0.7.5 /uv /usr/local/bin/uv
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    UV_PROJECT_ENVIRONMENT=/app
COPY . src
WORKDIR src
RUN uv sync \
    --locked \
    --no-dev \
    --no-editable

FROM python:3.12-slim
COPY --from=build --chown=app:app /app /app
USER app
WORKDIR /app
CMD ["fastapi", "run", "src/growthbook_api/main.py", "--port", "80"]
