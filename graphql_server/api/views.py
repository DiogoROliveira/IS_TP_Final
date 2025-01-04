from django.http import JsonResponse
from rest_framework.views import APIView
from .schema import Query, Mutation
import json

class CitiesView(APIView):
    def post(self, request):
        try:
            body = json.loads(request.body) if request.body else {}
            search = body.get('search', None)
            cities = Query.resolve_cities(None, None, search)
            formatted_cities = [
                {
                    'nome': city.nome,
                    'latitude': city.latitude,
                    'longitude': city.longitude,
                    'id': city.id
                } for city in cities
            ]
            return JsonResponse({'data': { 'cities': formatted_cities }})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
            

class UpdateCity(APIView):
    def post(self, request, id=None):
        data = json.loads(request.body)
        try:
            result = Mutation.update_city.mutate(None, None, 
                id=int(id), 
                latitude=data.get('latitude'),
                longitude=data.get('longitude')
            )
            return JsonResponse({'data': { 
                'city': {
                    'nome': result.city.nome,
                    'latitude': result.city.latitude,
                    'longitude': result.city.longitude,
                    'id': result.city.id
                }
            }})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)