FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

# Listens on HOST:HOST_PORT (defaults 0.0.0.0:9091) for analyzer connections
EXPOSE 9091

CMD ["python", "main.py"]
