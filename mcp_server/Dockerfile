# Use Python 3.13 slim as build stage
FROM python:3.13-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for building
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Production stage using distroless
FROM gcr.io/distroless/python3-debian12:latest

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/nonroot/.local

# Copy application code from builder stage
COPY --from=builder --chown=nonroot:nonroot /app /app

# Set working directory
WORKDIR /app

# Update PATH to include user packages
ENV PATH="/home/nonroot/.local/bin:${PATH}"
ENV PYTHONPATH="/app/.venv/bin:/app/"

# Use non-root user (built into distroless)
USER nonroot

# Expose port (adjust as needed)
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["python3", "mcp", "run", "server.py", "--transport", "http"]