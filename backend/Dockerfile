FROM python:3.13.6-slim

WORKDIR /app

# Create certs directory
RUN mkdir -p /app/certs

COPY backend/ .

# Copy certificates from build context
COPY certs/ca.crt /app/certs/
COPY certs/agentic-app.crt /app/certs/
COPY certs/agentic-app.key /app/certs/

# Set proper permissions for certificates
RUN chmod 644 /app/certs/ca.crt /app/certs/agentic-app.crt && \
    chmod 600 /app/certs/agentic-app.key

RUN pip install -U pip uv && uv sync --frozen --no-dev --no-editable

EXPOSE 7000

ENTRYPOINT ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "7000"]