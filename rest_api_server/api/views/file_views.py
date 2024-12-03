from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.file_serializer import FileUploadSerializer
import grpc
import api.grpc.server_services_pb2 as server_services_pb2
import api.grpc.server_services_pb2_grpc as server_services_pb2_grpc
import os
from rest_api_server.settings import GRPC_PORT, GRPC_HOST

class FileUploadView(APIView):
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            if not file:
                return Response({"error": "No file uploaded"}, status=400)
            
            # Get MIME type using mimetypes
            file_name, file_extension = os.path.splitext(file.name)

            # Read the file content and convert it to base64
            file_content = file.read()
            
            # Connect to the gRPC service
            channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
            stub = server_services_pb2_grpc.SendFileServiceStub(channel)
        
            # Prepare gRPC request
            request = server_services_pb2.SendFileRequestBody(
            file_name=file_name,
            file_mime=file_extension,
            file=file_content
            )

            # Send file data to gRPC service
            try:
                response = stub.SendFile(request)
                return Response({
                    "file_name": file_name,
                    "file_extension": file_extension
                }, status=status.HTTP_201_CREATED)
            
            except grpc.RpcError as e:
                return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
