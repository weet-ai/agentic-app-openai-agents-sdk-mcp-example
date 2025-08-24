FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Configure the Python directory so it is consistent
ENV UV_PYTHON_INSTALL_DIR=/python

# Only use the managed Python version
ENV UV_PYTHON_PREFERENCE=only-managed

# Install Python before the project for caching
RUN uv python install 3.13

WORKDIR /app

# Create certs directory
RUN mkdir -p /app/certs

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=mcp_server/uv.lock,target=uv.lock \
    --mount=type=bind,source=mcp_server/pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Copy application code
COPY mcp_server/ .

# Copy certificates into builder stage
COPY certs/ca.crt /app/certs/
COPY certs/server.crt /app/certs/
COPY certs/server.key /app/certs/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Then, use a final image without uv
FROM gcr.io/distroless/cc

# Copy the Python version
COPY --from=builder --chown=python:python /python /python

WORKDIR /app

# Copy the application from the builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/src /app/src
COPY --from=builder --chown=app:app /app/data /app/data

# Copy certificates from builder
COPY --from=builder --chown=app:app /app/certs /app/certs

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/"

EXPOSE 8000

CMD ["python", "src/api/server.py"]