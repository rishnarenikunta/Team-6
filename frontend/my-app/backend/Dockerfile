FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential gcc g++ python3-dev && \
    rm -rf /var/lib/apt/lists/*


COPY . .
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app
EXPOSE 8080

# Use exec and fallback port
CMD exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}