import pika
import os
import logging
from io import StringIO
import pandas as pd
import pg8000
from sqlalchemy import create_engine, Column, Integer, String, Float, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PW = os.getenv("RABBITMQ_PW", "guest")

QUEUE_NAME = 'csv_chunks'

DBHOST = os.getenv('DBHOST', 'localhost')
DBUSERNAME = os.getenv('DBUSERNAME', 'postgres')
DBPASSWORD = os.getenv('DBPASSWORD', 'postgres')
DBNAME = os.getenv('DBNAME', 'mydatabase')
DBPORT = int(os.getenv('DBPORT', '5432'))

# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger()

reassembled_data = []

Base = declarative_base()

class TemperatureData(Base):
    __tablename__ = 'data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    Region = Column(String(255), nullable=False)
    Country = Column(String(255), nullable=False)
    State = Column(String(255), nullable=True)
    City = Column(String(255), nullable=False)
    Month = Column(Integer, nullable=False)
    Day = Column(Integer, nullable=False)
    Year = Column(Integer, nullable=False)
    AvgTemperature = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint('Region', 'Country', 'State', 'City', 'Month', 'Day', 'Year', 
                         name='uq_temperature_data'),
    )

def get_db_connection_string(
    host=DBHOST, 
    database=DBNAME, 
    user=DBUSERNAME, 
    password=DBPASSWORD, 
    port=DBPORT
):
    return f"postgresql+pg8000://{user}:{password}@{host}:{port}/{database}"

@contextmanager
def db_session_scope(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error on database transaction: {e}")
        raise
    finally:
        session.close()

def insert_to_db_efficient(df, batch_size=1000):
    try:
        connection_string = get_db_connection_string()
        engine = create_engine(
            connection_string, 
            pool_size=10, 
            max_overflow=20,  
            pool_timeout=30,  
            pool_recycle=1800  
        )

        Base.metadata.create_all(engine)

        data_to_insert = df.to_dict('records')

        with db_session_scope(engine) as session:
            for i in range(0, len(data_to_insert), batch_size):
                batch = data_to_insert[i:i+batch_size]
                
                stmt = insert(TemperatureData).values(batch)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=[
                        'Region', 'Country', 'State', 'City',
                        'Month', 'Day', 'Year'
                    ]
                )
                session.execute(stmt)

        logger.info(f"Data inserted successfully: {len(data_to_insert)} records")
        return len(data_to_insert)

    except Exception as e:
        logger.error(f"Error inserting data: {e}")
        raise


def process_message(ch, method, properties, body):
    str_stream = body.decode('utf-8')

    if str_stream == "__EOF__":

        logger.info("EOF marker received. Finalizing...")
        
        try:
            file_content = b"".join(reassembled_data)
            csvfile = StringIO(file_content.decode('utf-8'))
            
            for df_chunk in pd.read_csv(csvfile, chunksize=10000):  
                logger.info(f"Processing chunk of size: {df_chunk.shape}")
                insert_to_db_efficient(df_chunk)

        except Exception as e:
            logger.error(f"Error processing final message: {e}")
        finally:
            reassembled_data.clear()
    else:
        reassembled_data.append(body)


def main():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT, 
        credentials=credentials,
        heartbeat=120
        )
    )

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_consume(queue=QUEUE_NAME,
                          
    on_message_callback=process_message, auto_ack=True)
    logger.info(f"Waiting for messages...", exc_info=True)
    channel.start_consuming()

if __name__ == "__main__":
    main()
