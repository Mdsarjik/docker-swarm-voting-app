# ── Vote App ──────────────────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="Sharjik Ahamed <ahamedsarjik54@gmail.com>"
LABEL description="Vote service — Flask app that collects votes and pushes to Redis"

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Flask port
EXPOSE 80

# Run with gunicorn for production
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80", "--log-file", "-", "--access-logfile", "-", "--workers", "4", "--keep-alive", "0"]
