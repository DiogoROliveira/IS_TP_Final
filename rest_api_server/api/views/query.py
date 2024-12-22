from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import grpc
import re
import api.grpc.server_services_pb2 as server_services_pb2
import api.grpc.server_services_pb2_grpc as server_services_pb2_grpc
from rest_api_server.settings import GRPC_PORT, GRPC_HOST


class XPathFilterBy(APIView):
    def post(self, request):
        file_name = request.data.get('file_name')
        xpath_query = request.data.get('xpath_query')

        if not file_name or not xpath_query:
            return Response({
                "error": "File name and xpath query are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.GroupByServiceStub(channel)

        grpc_request = server_services_pb2.FilterRequest(
            file_name=file_name,
            xpath_query=xpath_query
        )

        try:
            response = stub.FilterXML(grpc_request)
            response.query_result = re.sub(r'\s+', ' ', response.query_result)
            response.query_result = re.sub(r'\n', '', response.query_result)
            return Response({
                "result": response.query_result
            }, status=status.HTTP_200_OK)
        except grpc.RpcError as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class XPathOrderBy(APIView):
    def post(self, request):
        file_name = request.data.get('file_name')
        order_by_xpath = request.data.get('order_by_xpath')
        ascending = request.data.get('ascending', True)

        if not file_name or not order_by_xpath:
            return Response({
                "error": "File name and order_by_xpath are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.GroupByServiceStub(channel)

        grpc_request = server_services_pb2.OrderRequest(
            file_name=file_name,
            order_by_xpath=order_by_xpath,
            ascending=ascending
        )

        try:
            response = stub.OrderXML(grpc_request)
            results = "".join(response.ordered_nodes)
            encapsulated_results = f"<OrderedResults>{results}</OrderedResults>"
            encapsulated_results = encapsulated_results.replace("\n", "")
            return Response({
                "result": encapsulated_results
            }, status=status.HTTP_200_OK)
        except grpc.RpcError as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class XPathGroupBy(APIView):
    def post(self, request):
        file_name = request.data.get('file_name')
        group_by_xpaths = request.data.get('group_by_xpaths')

        if not file_name or not group_by_xpaths:
            return Response({
                "error": "File name and group_by_xpaths are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        if any(xpath.startswith("/") for xpath in group_by_xpaths):
            return Response({
                "error": "group_by_xpaths must not start with '/' or '//' instead start with './/'. "
            }, status=status.HTTP_400_BAD_REQUEST)


        if not isinstance(group_by_xpaths, list):
            return Response({
                "error": "group_by_xpaths must be a string list"
            }, status=status.HTTP_400_BAD_REQUEST)

        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.GroupByServiceStub(channel)

        grpc_request = server_services_pb2.GroupRequest(
            file_name=file_name,
            group_by_xpaths=group_by_xpaths
        )

        try:
            response = stub.GroupXML(grpc_request)

            grouped_data = {key: value for key, value in response.grouped_data.items()}

            return Response({
                "result": grouped_data
            }, status=status.HTTP_200_OK)
        except grpc.RpcError as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class XPathSearch(APIView):
    def post(self, request):
        file_name = request.data.get('file_name')
        search_term = request.data.get('search_term')

        if not file_name or not search_term:
            return Response({
                "error": "File name and search_term are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.GroupByServiceStub(channel)

        grpc_request = server_services_pb2.SearchRequest(
            file_name=file_name,
            search_term=search_term,
        )

        try:
            response = stub.SearchXML(grpc_request)

            results = "".join(response.matching_nodes)
            encapsulated_results = f"<SearchResults>{results}</SearchResults>"

            return Response({
                "result": encapsulated_results
            }, status=status.HTTP_200_OK)
        except grpc.RpcError as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
