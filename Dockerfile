# TSA Wait Times Twitter Bot - Docker Configuration
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (only production deps)
RUN pip install --no-cache-dir \
    beautifulsoup4==4.12.3 \
    requests==2.31.0 \
    tweepy==4.14.0 \
    python-dotenv==1.0.1 \
    urllib3==2.2.1

# Copy application code
COPY time2wait.py .

# Create non-root user for security
RUN useradd -m -u 1000 tsabot && \
    chown -R tsabot:tsabot /app

# Switch to non-root user
USER tsabot

# Health check
HEALTHCHECK --interval=5m --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('https://www.atl.com/times/', timeout=5)" || exit 1

# Run the bot
CMD ["python", "-u", "time2wait.py"]
