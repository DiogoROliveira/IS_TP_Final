import os

# Server Configuration
GRPC_SERVER_PORT = os.getenv('GRPC_SERVER_PORT', '50052')
MAX_WORKERS = int(os.getenv('MAX_WORKERS', '10'))

#Media Files
MEDIA_PATH=os.getenv('MEDIA_PATH', f'{os.getcwd()}/app/csv')

#DB settings
DBNAME=os.getenv('DBNAME', 'mydatabase')
DBUSERNAME=os.getenv('DBUSERNAME', 'myuser')
DBPASSWORD=os.getenv('DBPASSWORD', 'mypassword')
DBHOST=os.getenv('DBHOST', 'localhost')
DBPORT=os.getenv('DBPORT', '5432')
