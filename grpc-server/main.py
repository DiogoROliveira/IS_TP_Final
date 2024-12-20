from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PW
from concurrent import futures
import os
import server_services_pb2_grpc
import server_services_pb2
import grpc
import pika
import time
import logging
import requests
import xml.etree.ElementTree as ET
import xmlschema
from lxml import etree
from lxml.etree import Element, SubElement
import pandas as pd

# BUUUUUUHHH

# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("FileService")

# ====================== Functions ======================

def csv_to_xml(csv_file, xml_file, objname):
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo {csv_file} não encontrado.")

    df['latitude'] = None
    df['longitude'] = None

    for idx, row in df.iterrows():
        if 'City' in row: 
            lat, lon = get_lat_lon_from_city(row['City'])
            df.at[idx, 'latitude'] = lat
            df.at[idx, 'longitude'] = lon

    root = Element('root')
 
    for _, row in df.iterrows():
        obj_element = SubElement(root, objname)
        for col_name, value in row.items():
            col_element = SubElement(obj_element, col_name)
            col_element.text = str(value) if pd.notna(value) else ''

    tree = etree.ElementTree(root)
    tree.write(xml_file, pretty_print=True, xml_declaration=True, encoding='UTF-8')

def fill_empty_fields(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for airport in root.findall("Temp"):
        for field in airport:
            if field.text is None or field.text.strip() == "":
                field.text = "null"

    tree.write(xml_file, encoding='utf-8', xml_declaration=True)

def validate_xml(xml_file, xsd_file):
    try:
        schema = xmlschema.XMLSchema(xsd_file)
        return schema.is_valid(xml_file)
    except Exception as e:
        logger.error(f"XML Validation Error: {str(e)}")
        return False

cache = {}

def get_lat_lon_from_city(city):
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
            return None, None
    except Exception as e:
        logger.error(f"Error fetching latitude and longitude: {str(e)}")
        return None, None


# ======================= gRPC Services =======================

class ImporterService(server_services_pb2_grpc.ImporterServiceServicer):
    def __init__(self, *args, **kwargs):
        pass

    def UploadCSV(self, request, context):
        try:
            os.makedirs(MEDIA_PATH, exist_ok=True)
            file_path = os.path.join(MEDIA_PATH, "./csv/", request.file_name + request.file_mime)

            ficheiro_em_bytes = request.file

            with open(file_path, 'wb') as f:
                f.write(ficheiro_em_bytes)
            
            logger.info(f"File {request.file_name} uploaded successfully")
            return server_services_pb2.FileUploadResponse(success=True)
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            context.set_details(f"Failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.FileUploadResponse(success=False)   

    def UploadCSVChunks(self, request_iterator, context):
        try:
            # rabbitmq connection
            rabbit_connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST, 
                    port=RABBITMQ_PORT, 
                    credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW),
                    heartbeat=120
                )
            )
            rabbit_channel = rabbit_connection.channel()
            rabbit_channel.queue_declare(queue='csv_chunks')
            

            file_name = None
            file_chunks = []
            
            # reads the chunks
            for chunk in request_iterator:
                if not file_name:
                    file_name = chunk.file_name

                # appends recieved chunk to the list
                file_chunks.append(chunk.data)

                # sends the chunk to the queue
                rabbit_channel.basic_publish(exchange='', routing_key='csv_chunks', body=chunk.data)
            
            # marks the end of the file
            rabbit_channel.basic_publish(exchange='', routing_key='csv_chunks', body="__EOF__")

            file_content = b"".join(file_chunks)

            file_path = os.path.join(MEDIA_PATH, "./csv/", file_name)

            with open(file_path, 'wb') as f:
                f.write(file_content)

            # XML conversion and validation
            # ===================================================
            xml_path = os.path.join(MEDIA_PATH, "./xml/")
            csv_to_xml(file_path, os.path.join(xml_path, file_name.split(".")[0] + ".xml"), "Temp")
            xml_file = os.path.join(xml_path, file_name.split(".")[0] + ".xml")

            fill_empty_fields(xml_file)

            if not validate_xml(xml_file, os.path.join(MEDIA_PATH, "./schemas/", "schema.xsd")):
                logger.error(f"XML Validation Error")
            else:
                logger.info(f"XML Validation Success: {xml_file}")
            # ===================================================

            return server_services_pb2.FileUploadChunksResponse(
                success=True,
                message=f'File {file_name} was imported.'
            )
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return server_services_pb2.FileUploadChunksResponse(success=False, message=str(e))


class GroupByService(server_services_pb2_grpc.GroupByServiceServicer):
    def __init__(self, *args, **kwargs):
        pass

    def FilterXML(self, request, context):
        try:
            # validate request body
            if not request.file_name or not request.xpath_query:
                logger.error("Missing body parameters: file_name and/or xpath_query")
                raise ValueError("Missing body parameters: file_name and/or xpath_query")

            xml_path = os.path.join(MEDIA_PATH, "./xml/")
            xml_file = os.path.join(xml_path, request.file_name)

            # validate file exists
            if not os.path.exists(xml_file):
                logger.error(f"File not found: {xml_file}")
                raise FileNotFoundError(f"File not found: {xml_file}")

            # xpath query
            tree = etree.parse(xml_file)
            root = tree.getroot()
            results = root.xpath(request.xpath_query)
            
            # convert results toString
            str_results = [
                etree.tostring(result, encoding='unicode', method='xml').strip() 
                for result in results
            ]
            
            logger.info(f"XPath query executed successfully: {len(results)} results")
            return server_services_pb2.FilterResponse(query_result=' '.join(str_results))
        
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return server_services_pb2.FilterResponse(query_result=str(e))

# ================== main ==================

def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Consult the file "server_services_pb2_grpc" to see the name of the function generated
    #to add the service to the server
    server_services_pb2_grpc.add_ImporterServiceServicer_to_server(ImporterService(), server)
    server_services_pb2_grpc.add_GroupByServiceServicer_to_server(GroupByService(), server)

    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    server.start()

    print(f'Server running at {GRPC_SERVER_PORT}...')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

