# ── Worker Service ────────────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="Sharjik Ahamed <ahamedsarjik54@gmail.com>"
LABEL description="Worker service — reads votes from Redis queue and writes to PostgreSQL"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .

CMD ["python", "-u", "worker.py"]
