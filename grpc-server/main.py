from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT
import pg8000
from concurrent import futures
import os
import server_services_pb2_grpc
import server_services_pb2
import grpc
import csv
import logging
import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils
from xml.dom import minidom
from lxml import etree
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


# ============== gRPC Services ==============

class SendFileService(server_services_pb2_grpc.SendFileServiceServicer):

    def __init__(self, *args, **kwargs):
        pass


    def SendFile(self, request, context):
        os.makedirs(MEDIA_PATH, exist_ok=True)
        file_path = os.path.join(MEDIA_PATH, "./csv/", request.file_name + request.file_mime)

        ficheiro_em_bytes = request.file

        with open(file_path, 'wb') as f:
            f.write(ficheiro_em_bytes)
        
        logger.info(f"{DBHOST}:{DBPORT}", exc_info=True)
        # Establish connection to PostgreSQL
        try:
            # Connect to the database
            conn = pg8000.connect(user=f'{DBUSERNAME}', password=f'{DBPASSWORD}', host=f'{DBHOST}', port=f'{DBPORT}', database=f'{DBNAME}')
            cursor = conn.cursor()
            
            #SQL query to create a table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS data (
                id SERIAL PRIMARY KEY,
                ident VARCHAR(100),
                type VARCHAR(100) NOT NULL,
                name VARCHAR(100) NOT NULL,
                latitude_deg FLOAT,
                longitude_deg FLOAT,
                elevation_ft INT,
                continent VARCHAR(100),
                iso_country VARCHAR(100),
                iso_region VARCHAR(100),
                municipality VARCHAR(100),
                scheduled_service VARCHAR(100),
                gps_code VARCHAR(100),
                local_code VARCHAR(100)
            );
            """

            # Read the CSV file
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                next(reader)  # Skip the header row
                for row in reader:

                    # SQL query to insert data into the table
                    insert_query = """
                    INSERT INTO data (ident, type, name, latitude_deg, longitude_deg, elevation_ft, 
                    continent, iso_country, iso_region, municipality, scheduled_service, gps_code, local_code)
                    SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM data WHERE ident = %s
                    );
                    """

                    cursor.execute(insert_query, (
                        row['ident'],
                        row['type'],
                        row['name'],
                        float(row['latitude_deg']) if row['latitude_deg'] else None,
                        float(row['longitude_deg']) if row['longitude_deg'] else None,
                        int(row['elevation_ft']) if row['elevation_ft'] else None,
                        row['continent'],
                        row['iso_country'],
                        row['iso_region'],
                        row['municipality'],
                        row['scheduled_service'],
                        row['gps_code'] if row['gps_code'] else None,
                        row['local_code'] if row['local_code'] else None,
                        row['ident']
                    ))

            # Execute the SQL query to create the table
            cursor.execute(create_table_query)
            # Commit the changes (optional in this case since it's a DDL query)
            conn.commit()
            return server_services_pb2.SendFileResponseBody(success=True)
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            context.set_details(f"Failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.SendFileResponseBody(success=False)
        
class ImporterService(server_services_pb2_grpc.ImporterServiceServicer):
    def __init__(self, *args, **kwargs):
        pass

    def UploadCSV(self, request, context):
        os.makedirs(MEDIA_PATH, exist_ok=True)
        file_path = os.path.join(MEDIA_PATH, "./csv/", request.file_name + request.file_mime)

        ficheiro_em_bytes = request.file

        with open(file_path, 'wb') as f:
            f.write(ficheiro_em_bytes)
        
        logger.info(f"{DBHOST}:{DBPORT}", exc_info=True)
        # Establish connection to PostgreSQL
        try:
            # Connect to the database
            conn = pg8000.connect(user=f'{DBUSERNAME}', password=f'{DBPASSWORD}', host=f'{DBHOST}', port=f'{DBPORT}', database=f'{DBNAME}')
            cursor = conn.cursor()
            
            #SQL query to create a table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS data (
                id SERIAL PRIMARY KEY,
                ident VARCHAR(100),
                type VARCHAR(100) NOT NULL,
                name VARCHAR(100) NOT NULL,
                latitude_deg FLOAT,
                longitude_deg FLOAT,
                elevation_ft INT,
                continent VARCHAR(100),
                iso_country VARCHAR(100),
                iso_region VARCHAR(100),
                municipality VARCHAR(100),
                scheduled_service VARCHAR(100),
                gps_code VARCHAR(100),
                local_code VARCHAR(100)
            );
            """

            # Read the CSV file
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                next(reader)  # Skip the header row
                for row in reader:

                    # SQL query to insert data into the table
                    insert_query = """
                    INSERT INTO data (ident, type, name, latitude_deg, longitude_deg, elevation_ft, 
                    continent, iso_country, iso_region, municipality, scheduled_service, gps_code, local_code)
                    SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM data WHERE ident = %s
                    );
                    """

                    cursor.execute(insert_query, (
                        row['ident'],
                        row['type'],
                        row['name'],
                        float(row['latitude_deg']) if row['latitude_deg'] else None,
                        float(row['longitude_deg']) if row['longitude_deg'] else None,
                        int(row['elevation_ft']) if row['elevation_ft'] else None,
                        row['continent'],
                        row['iso_country'],
                        row['iso_region'],
                        row['municipality'],
                        row['scheduled_service'],
                        row['gps_code'] if row['gps_code'] else None,
                        row['local_code'] if row['local_code'] else None,
                        row['ident']
                    ))

            # Execute the SQL query to create the table
            cursor.execute(create_table_query)
            # Commit the changes (optional in this case since it's a DDL query)
            conn.commit()
            return server_services_pb2.FileUploadResponse(success=True)
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            context.set_details(f"Failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.FileUploadResponse(success=False)   

    def ConvertToXML(self, request, context):
        try:
           # Ensure absolute paths are used
            base_media_path = os.path.abspath(MEDIA_PATH)
            
            # Create directories using absolute paths
            csv_dir = os.path.join(base_media_path, "csv")
            xml_dir = os.path.join(base_media_path, "xml")
            
            os.makedirs(base_media_path, exist_ok=True)
            os.makedirs(csv_dir, exist_ok=True)
            os.makedirs(xml_dir, exist_ok=True)

            # Construct file paths using absolute paths
            input_csv_path = os.path.join(csv_dir, request.file_name + request.file_mime)
            xml_output_path = os.path.join(xml_dir, f"{os.path.splitext(request.file_name)[0]}.xml")
            
            # Debugging: Log the paths
            logger.info(f"Base Media Path: {base_media_path}")
            logger.info(f"Input CSV Path: {input_csv_path}")
            logger.info(f"XML Output Path: {xml_output_path}")
            
            # Check if input file exists
            if not os.path.exists(input_csv_path):
                logger.error(f"Input file not found: {input_csv_path}")
                context.set_details("Input file not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return server_services_pb2.XMLFileResponse(success=False)

            # Convert CSV to XML
            csv_to_xml(input_csv_path, xml_output_path, "Temp")
            
            # Fill empty fields
            fill_empty_fields(xml_output_path)
            
            # Validate XML (optional, you can add a schema path)
            xsd_path = os.path.join(os.path.dirname(__file__), 'schemas', 'schema.xsd')
            if os.path.exists(xsd_path):
                if not validate_xml(xml_output_path, xsd_path):
                    logger.warning(f"XML validation failed for {xml_output_path}")
                            
            logger.info(f"XML validation passed for {xml_output_path}")

            
            return server_services_pb2.XMLFileResponse(success=True)
        except Exception as e:
            logger.error(f"XML Conversion Error: {str(e)}", exc_info=True)
            context.set_details(f"Failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.XMLFileResponse(success=False)
        
    def CheckConversionStatus(self, request, context):
        pass

    def DownloadXML(self, request, context):
        pass


# ============= main ==============

def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Consult the file "server_services_pb2_grpc" to see the name of the function generated
    #to add the service to the server

    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)
    server_services_pb2_grpc.add_ImporterServiceServicer_to_server(ImporterService(), server)

    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    server.start()

    print(f'Server running at {GRPC_SERVER_PORT}...')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

