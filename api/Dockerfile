# ---- Stage 1: Builder ----
# We use a full Python image to install dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy only requirements first (Docker caches this layer if requirements don't change)
COPY requirements.txt .

# Install dependencies into a separate folder so we can copy only them later
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: Final Image ----
# We start fresh with a slim image (no build tools = smaller, safer image)
FROM python:3.11-slim

# BUG FIX PRACTICE: Never run as root in production containers
# Create a non-root user called "appuser"
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Tell Docker this container listens on port 8000
EXPOSE 8000

# HEALTHCHECK: Docker will run this command every 30s to check if API is alive
# If it fails 3 times in a row, Docker marks the container as "unhealthy"
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start the API server
# --host 0.0.0.0 means "accept connections from anywhere" (required in Docker)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]