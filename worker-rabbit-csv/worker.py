import pika
import json
import os
import logging
from io import StringIO
import pandas as pd
import pg8000

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PW = os.getenv("RABBITMQ_PW", "guest")

QUEUE_NAME = 'csv_chunks'

DBHOST = os.getenv('DBHOST', 'localhost')
DBUSERNAME = os.getenv('DBUSERNAME', 'postgres')
DBPASSWORD = os.getenv('DBPASSWORD', 'postgres')
DBNAME = os.getenv('DBNAME', 'mydatabase')
DBPORT = os.getenv('DBPORT', '5432')

# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger()

reassembled_data = []

def process_message(ch, method, properties, body):

    # body is a CSV chunk.
    str_stream = body.decode('utf-8')
    
    if str_stream == "__EOF__":
        
        print("EOF marker received. Finalizing...")
        file_content = b"".join(reassembled_data)
        csv_text = file_content.decode('utf-8')
    
        if len(reassembled_data) > 1:
        
            csvfile = StringIO(csv_text)
            df = pd.read_csv(csvfile)
            print(df)
            #call a function to save the df data to a database
            
            conn = pg8000.connect(
            host=DBHOST,
            database=DBNAME,
            user=DBUSERNAME,
            password=DBPASSWORD,
            port=int(DBPORT)
            )

            cursor = conn.cursor()

            create_table_query = """
                CREATE TABLE IF NOT EXISTS data (
                    id SERIAL PRIMARY KEY,
                    Region VARCHAR(255) NOT NULL,
                    Country VARCHAR(255) NOT NULL,
                    State VARCHAR(255),
                    City VARCHAR(255) NOT NULL,
                    Month INT NOT NULL,
                    Day INT NOT NULL,
                    Year INT NOT NULL,
                    AvgTemperature FLOAT NOT NULL
                );
            """

            cursor.execute(create_table_query)


             # Processar cada linha do DataFrame e inserir os dados
            for _, row in df.iterrows():
                # Verifica duplicatas no banco
                cursor.execute(
                    "SELECT 1 FROM data WHERE Region=%s AND Country=%s AND State=%s AND City=%s AND Month=%s AND Day=%s AND Year=%s AND AvgTemperature=%s",
                    (row["Region"], row["Country"], row["State"], row["City"], row["Month"], row["Day"], row["Year"], row["AvgTemperature"])
                )
                if not cursor.fetchone():
                    # Inserir a linha se não for duplicada
                    cursor.execute(
                        "INSERT INTO data (Region, Country, State, City, Month, Day, Year, AvgTemperature) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (row["Region"], row["Country"], row["State"], row["City"], row["Month"], row["Day"], row["Year"], row["AvgTemperature"])
                    )

            # Commit das mudanças
            conn.commit()
            cursor.close()
            conn.close()

            reassembled_data.clear()
    else:
        print(body)
        reassembled_data.append(body)


def main():
    
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW)
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST, 
            port=RABBITMQ_PORT, 
            credentials=credentials
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
