from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from .schema import Query

# Create your views here.

class CitiesView(APIView):
    def post(self, request):
        cities = Query.resolve_cities(None, None, None)
        formatted_cities = [
            {
                'nome': city.nome,
                'latitude': city.latitude,
                'longitude': city.longitude,
                'id': city.id
            } for city in cities
        ]
        return JsonResponse({'data': { 'cities': formatted_cities }})
    
    def put(self, request):
        return JsonResponse({'message': 'PUT request received'})