FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

COPY wait_for_rabbit.py /usr/local/bin/wait_for_rabbit.py

EXPOSE 8003

CMD ["sh", "-c", "python /usr/local/bin/wait_for_rabbit.py rabbitmq 5672 && python worker.py"]