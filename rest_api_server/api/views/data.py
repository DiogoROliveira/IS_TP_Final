from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection


class GetAllData(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM data")
            result = cursor.fetchall()

            data = [Book(id=row[0], name=row[2]) for row in result]

            return Response({"data": data}, status=status.HTTP_200_OK)
