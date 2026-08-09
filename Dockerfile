# ── Inside Airbnb Gent Dashboard — Production Docker Image ──

FROM python:3.11-slim

LABEL org.opencontainers.image.title="Inside Airbnb Gent Dashboard"
LABEL org.opencontainers.image.description="Business intelligence dashboard for Airbnb housing market analytics"
LABEL org.opencontainers.image.source="https://github.com/twomathematicians-code/inside-airbnb-gent-dashboard"

# Install system deps for Plotly image export
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn kaleido

# Copy application code
COPY src/ ./src/
COPY assets/ ./assets/
COPY README.md LICENSE ./

WORKDIR /app/src

# Expose port (default 8051, overridable via PORT env var)
EXPOSE 8051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8051}/ || exit 1

# Production: 2 workers, threaded
CMD gunicorn app:server \
    --bind 0.0.0.0:${PORT:-8051} \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
