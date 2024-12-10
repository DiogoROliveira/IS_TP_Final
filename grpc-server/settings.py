import os

# Server Configuration
GRPC_SERVER_PORT = os.getenv('GRPC_SERVER_PORT', '50052')
MAX_WORKERS = int(os.getenv('MAX_WORKERS', '10'))

#Media Files
MEDIA_PATH=os.getenv('MEDIA_PATH', f'{os.getcwd()}/media')

#DB settings
DBNAME=os.getenv('DBNAME', 'mydatabase')
DBUSERNAME=os.getenv('DBUSERNAME', 'postgres')
DBPASSWORD=os.getenv('DBPASSWORD', 'postgres')
DBHOST=os.getenv('DBHOST', 'localhost')
DBPORT=os.getenv('DBPORT', '5432')

#RabbitMQ settings
RABBITMQ_HOST=os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT=os.getenv('RABBITMQ_PORT', '5672')
RABBITMQ_USER=os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PW=os.getenv('RABBITMQ_PW', 'guest')
