import socket
import time
import sys

def wait_for_rabbitmq(host, port, retries=10, delay=5):
    for attempt in range(retries):
        try:
            with socket.create_connection((host, port), timeout=5):
                print(f"RabbitMQ is ready at {host}:{port}!")
                return
        except (socket.error, socket.timeout):
            print(f"Attempt {attempt + 1}/{retries}: RabbitMQ not ready, retrying in {delay} seconds...")
            time.sleep(delay)
    print(f"RabbitMQ is not ready after {retries} attempts, exiting.")
    sys.exit(1)

if __name__ == "__main__":
    rabbitmq_host = sys.argv[1]
    rabbitmq_port = int(sys.argv[2])
    wait_for_rabbitmq(rabbitmq_host, rabbitmq_port)