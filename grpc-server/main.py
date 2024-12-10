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
from lxml import etree
import xml.sax.saxutils as saxutils
import xmlschema


# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("FileService")

# =============== Functions =================

def csv_to_xml(csv_file, xml_file, objname, chunk_size=10000):
    
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Arquivo {csv_file} não encontrado.")

    
    with open(xml_file, mode='w', encoding='utf-8') as xmlfile:
        # initial root tag
        xmlfile.write('<?xml version="1.0" encoding="UTF-8"?>\n<root>\n')

        with open(csv_file, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            headers = reader.fieldnames

            chunk = []
            for line in reader:
                chunk.append(line)

                # saves chunk if it's full
                if len(chunk) >= chunk_size:
                    
                    for item in chunk:
                        xmlfile.write('  <' + objname + '>\n')
                        for field in headers:
                            # process special chars
                            value = str(item[field]) if item[field] is not None else ''
                            escaped_value = saxutils.escape(value)
                            xmlfile.write(f'    <{field}>{escaped_value}</{field}>\n')
                        xmlfile.write('  </' + objname + '>\n')
                    
                    # reset chunk
                    chunk = []

            # leftover chunk (less than 10k lines)
            if chunk:
                for item in chunk:
                    xmlfile.write('  <' + objname + '>\n')
                    for field in headers:
                        value = str(item[field]) if item[field] is not None else ''
                        escaped_value = saxutils.escape(value)
                        xmlfile.write(f'    <{field}>{escaped_value}</{field}>\n')
                    xmlfile.write('  </' + objname + '>\n')

        xmlfile.write('</root>')

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
                    credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW)
                )
            )

            rabbit_channel = rabbit_connection.channel()
            rabbit_channel.queue_declare(queue='csv_chunks')
            
            csv_path = os.path.join(MEDIA_PATH, "./csv/")
            xml_path = os.path.join(MEDIA_PATH, "./xml/")
            os.makedirs(csv_path, exist_ok=True)

            file_name = None
            file_chunks = [] # Store all chunks in memory
            
            for chunk in request_iterator:
                if not file_name:
                    file_name = chunk.file_name
                    
                # Collect the file data chunks
                file_chunks.append(chunk.data)

                # Send data chunk to the worker
                rabbit_channel.basic_publish(exchange='', routing_key='csv_chunks', body=chunk.data)

            # Send info that the file stream ended
            rabbit_channel.basic_publish(exchange='', routing_key='csv_chunks', body="__EOF__")

            # Combine all chunks into a single bytes object
            file_content = b"".join(file_chunks)
            
            file_path = os.path.join(csv_path, file_name)

            with open(file_path, "wb") as f:
                f.write(file_content)

            try:
                xml_file = os.path.join(xml_path, f"{os.path.splitext(file_name)[0]}.xml")
                csv_to_xml(file_path, xml_file, "Temp")
                fill_empty_fields(xml_file)

                if not validate_xml(xml_file, "schemas/schema.xsd"):
                    logger.warning(f"XML validation failed for {xml_file}")
                else:
                    logger.info(f"XML validation successful for {xml_file}")
            except Exception as e:
                logger.error(f"Error: {str(e)}", exc_info=True)
                return server_services_pb2.FileUploadChunksResponse(success=False, message=str(e))
            
            return server_services_pb2.FileUploadChunksResponse(success=True, message='File Imported')
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

