from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT, RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PW
import pg8000
from concurrent import futures
import os
import server_services_pb2_grpc
import server_services_pb2
import grpc
import csv
import pika
import logging
import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils
import xmlschema
from lxml import etree
from lxml.etree import Element, SubElement, tostring
import pandas as pd


# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("FileService")

# =============== Functions =================

def csv_to_xml(csv_file, xml_file, objname):
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo {csv_file} não encontrado.")

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


# ================== gRPC Services ==================

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
            
            logger.info(f"{DBHOST}:{DBPORT}", exc_info=True)
        
            return server_services_pb2.FileUploadResponse(success=True)
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            context.set_details(f"Failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.FileUploadResponse(success=False)   

    def UploadCSVChunks(self, request_iterator, context):
        try:
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
            
            for chunk in request_iterator:
                if not file_name:
                    file_name = chunk.file_name

                file_chunks.append(chunk.data)

                # Sends the chunk to the queue
                rabbit_channel.basic_publish(exchange='', routing_key='csv_chunks', body=chunk.data)
            
            # Marks the end of the file
            rabbit_channel.basic_publish(exchange='', routing_key='csv_chunks', body="__EOF__")

            file_content = b"".join(file_chunks)

            file_path = os.path.join(MEDIA_PATH, "./csv/", file_name)

            with open(file_path, 'wb') as f:
                f.write(file_content)

            xml_path = os.path.join(MEDIA_PATH, "./xml/")
            csv_to_xml(file_path, os.path.join(xml_path, file_name.split(".")[0] + ".xml"), "Temp")
            xml_file = os.path.join(xml_path, file_name.split(".")[0] + ".xml")

            fill_empty_fields(xml_file)

            if not validate_xml(xml_file, os.path.join(MEDIA_PATH, "./schemas/", "schema.xsd")):
                logger.error(f"XML Validation Error: {str(e)}")
            else:
                logger.info(f"XML Validation Success: {xml_file}")
            
            return server_services_pb2.FileUploadChunksResponse(
                success=True,
                message=f'File {file_name} was imported.'
            )
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return server_services_pb2.FileUploadChunksResponse(success=False, message=str(e))

# ============= main ==============

def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Consult the file "server_services_pb2_grpc" to see the name of the function generated
    #to add the service to the server
    server_services_pb2_grpc.add_ImporterServiceServicer_to_server(ImporterService(), server)

    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    server.start()

    print(f'Server running at {GRPC_SERVER_PORT}...')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

