FROM python:3.11-slim

WORKDIR /app

COPY . /app/

RUN apt-get update && apt-get install -y \
    libpq-dev gcc --no-install-recommends && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 8003

CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]