from concurrent import futures
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH
import os
import server_services_pb2_grpc
import server_services_pb2
import grpc
#Consult the file "server_services_pb2_grpc" to find out the name of the Servicer class of
#the "SendFileService" service

class SendFileService(server_services_pb2_grpc.SendFileServiceServicer):

    def __init__(self, *args, **kwargs):
        pass


    def SendFile(self, request, context):
        os.makedirs(MEDIA_PATH, exist_ok=True)
        file_path = os.path.join(MEDIA_PATH, request.file_name + request.file_mime)


        ficheiro_em_bytes = request.file


        with open(file_path, 'wb') as f:
            f.write(ficheiro_em_bytes)
        
        #nome definido no proto para a resposta "SendFileResponseBody"
        return server_services_pb2.SendFileResponseBody(success=True)
        

def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Consult the file "server_services_pb2_grpc" to see the name of the function generated
    #to add the service to the server

    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)

    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    server.start()

    print(f'Server running at {GRPC_SERVER_PORT}...')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()