from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import grpc
import re
import api.grpc.server_services_pb2 as server_services_pb2
import api.grpc.server_services_pb2_grpc as server_services_pb2_grpc
from rest_api_server.settings import GRPC_PORT, GRPC_HOST


class XPathQueryView(APIView):
    def post(self, request):
        # extract body info
        file_name = request.data.get('file_name')
        xpath_query = request.data.get('xpath_query')

        # validate request body
        if not file_name or not xpath_query:
            return Response({
                "error": "Nome do arquivo e consulta XPath são obrigatórios"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # connection to gRPC
        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.GroupByServiceStub(channel)

        # prepare gRPC request
        request = server_services_pb2.FilterRequest(
            file_name=file_name,
            xpath_query=xpath_query
        )

        # send request to gRPC
        try:
            response = stub.FilterXML(request)
            cleaned_result = re.sub(r'\s+', ' ', response.query_result).strip()
            return Response({
                "result": cleaned_result
            }, status=status.HTTP_200_OK)
        except grpc.RpcError as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)