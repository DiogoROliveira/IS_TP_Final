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
                    "ident": row[1],
                    "type": row[2],
                    "name": row[3],
                    "latitude_deg": row[4],
                    "longitude_deg": row[5],
                    "elevation_ft": row[6],
                    "continent": row[7],
                    "iso_country": row[8],
                    "iso_region": row[9],
                    "municipality": row[10],
                    "scheduled_service": row[11],
                    "gps_code": row[12],
                    "local_code": row[13],
                }
                for row in result
            ]

            return Response({"data": data}, status=status.HTTP_200_OK)
