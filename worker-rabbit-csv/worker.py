import pika
import os
import logging
from io import StringIO
import pandas as pd
import pg8000
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker, relationship
from contextlib import contextmanager
import requests
import time


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

# ====================== DB Setup ======================

Base = declarative_base()

# DB table models
class Country(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)

class TemperatureData(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    Region = Column(String(255), nullable=False)
    Country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    State = Column(String(255), nullable=True)
    City = Column(String(255), nullable=False)
    Month = Column(Integer, nullable=False)
    Day = Column(Integer, nullable=False)
    Year = Column(Integer, nullable=False)
    AvgTemperature = Column(Float, nullable=False)
    Latitude = Column(Float, nullable=False)
    Longitude = Column(Float, nullable=False)

    # Relationship to the Country table
    country = relationship("Country")

    __table_args__ = (
        UniqueConstraint('Region', 'Country_id', 'State', 'City', 'Month', 'Day', 'Year', 
                         name='uq_temperature_data'),
    )

# DB connection
def get_db_connection_string(
    host=DBHOST, 
    database=DBNAME, 
    user=DBUSERNAME, 
    password=DBPASSWORD, 
    port=DBPORT
):
    return f"postgresql+pg8000://{user}:{password}@{host}:{port}/{database}"

# DB session
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


def insert_to_db(df, batch_size=1000):
    try:
        connection_string = get_db_connection_string()
        engine = create_engine(
            connection_string, 
            pool_size=10, 
            max_overflow=20,  
            pool_timeout=30,  
            pool_recycle=1800  
        )

        # create tables
        Base.metadata.create_all(engine)

        # creates empty lat and lon columns
        df['Latitude'] = None
        df['Longitude'] = None

        # populates lat and lon
        for idx, row in df.iterrows():
            if 'City' in row and 'Country' in row: 
                lat, lon = get_lat_lon_from_city(row['City'], row['Country'])
                df.at[idx, 'Latitude'] = lat
                df.at[idx, 'Longitude'] = lon

        data_to_insert = df.to_dict('records')

        with db_session_scope(engine) as session:
            # insert countries
            countries = {row['Country'] for row in data_to_insert}
            country_map = {}

            for country in countries:
                stmt = insert(Country).values(name=country).on_conflict_do_nothing()
                session.execute(stmt)

            session.commit() 

            # retrieve countries to map later to temps
            country_map = {
                country.name: country.id 
                for country in session.query(Country).all()
            }

            # map countries to ids in temp data
            for row in data_to_insert:
                row['Country_id'] = country_map[row.pop('Country')]

            # insert temps
            for i in range(0, len(data_to_insert), batch_size):
                batch = data_to_insert[i:i+batch_size]

                stmt = insert(TemperatureData).values(batch)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=[
                        'Region', 'Country_id', 'State', 'City',
                        'Month', 'Day', 'Year'
                    ]
                )
                session.execute(stmt)

        logger.info(f"Data inserted successfully: {len(data_to_insert)} records")
        return len(data_to_insert)

    except Exception as e:
        logger.error(f"Error inserting data: {e}")
        raise

# ========================================================

cache = {}

def get_lat_lon_from_city(city, country):
    try:
        if city in cache:
            logger.info(f"Cache hit for city: {city}")
            return cache[city]['lat'], cache[city]['lon']
        
        logger.info(f"Cache miss for city: {city}. Fetching data...")
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            "q": city,
            "format": 'json',
            "limit": 1,
        }
        headers = {
            "User-Agent": "GRPC-APP/1.0 (diogo.rosas.oliveira@ipvc.pt)"
        }

        time.sleep(1)
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data:
            lat, lon = data[0]['lat'], data[0]['lon']
            logger.info(f"Latitude: {lat}, Longitude: {lon}")
            cache[city] = {'lat': lat, 'lon': lon}
            return lat, lon
        else:
            params2 = {
                "q": country,
                "format": 'json',
                "limit": 1,
            }
            response = requests.get(url, params=params2, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data:
                lat, lon = data[0]['lat'], data[0]['lon']
                logger.info(f"Latitude: {lat}, Longitude: {lon}")
                cache[city] = {'lat': lat, 'lon': lon}
                return lat, lon
            else:
                return 0, 0

    except Exception as e:
        logger.error(f"Error fetching latitude and longitude: {str(e)}")
        return 0, 0


def process_message(ch, method, properties, body):
    str_stream = body.decode('utf-8')

    if str_stream == "__EOF__":

        logger.info("EOF marker received. Finalizing...")
        
        try:
            file_content = b"".join(reassembled_data)
            csvfile = StringIO(file_content.decode('utf-8'))
            
            for df_chunk in pd.read_csv(csvfile, chunksize=10000):  
                logger.info(f"Processing chunk of size: {df_chunk.shape}")
                insert_to_db(df_chunk)

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
        heartbeat=600
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

