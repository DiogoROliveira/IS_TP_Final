from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection


class GetAllData(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM data")
            result = cursor.fetchall()

            data = [
                {
                    "id": row[0],
                    "Region": row[1],
                    "Country": row[2],
                    "State": row[3],
                    "City": row[4],
                    "Month": row[5],
                    "Day": row[6],
                    "Year": row[7],
                    "AvgTemperature": row[8],
                }
                for row in result
            ]

            return Response({"data": data}, status=status.HTTP_200_OK)
