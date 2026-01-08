# Recession Dashboard - Production Docker Image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY web_app/requirements.txt /app/web_app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r web_app/requirements.txt

# Copy project files
COPY src/ /app/src/
COPY web_app/ /app/web_app/
COPY scripts/ /app/scripts/
COPY data/ /app/data/

# Create necessary directories
RUN mkdir -p /app/data/cache /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 dashboarduser && \
    chown -R dashboarduser:dashboarduser /app

# Switch to non-root user
USER dashboarduser

# Expose port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8050/ || exit 1

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8050", \
    "--workers", "4", \
    "--threads", "2", \
    "--timeout", "120", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--log-level", "info", \
    "web_app.app:server"]
