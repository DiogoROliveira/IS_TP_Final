import graphene
from graphene_django import DjangoObjectType

from .models import Temperature

class TemperatureType(DjangoObjectType):
    class Meta:
        model = Temperature
        fields = "__all__"


class CreateTemperature(graphene.Mutation):
    class Arguments:
        region = graphene.String(required=True)
        country = graphene.String(required=True)
        state = graphene.String(required=True)
        city = graphene.String(required=True)
        month = graphene.Int(required=True)
        day = graphene.Int(required=True)
        year = graphene.Int(required=True)
        avg_temperature = graphene.Float(required=True)
        latitude = graphene.Float(required=True)
        longitude = graphene.Float(required=True)
    
    temperature = graphene.Field(TemperatureType)

    def mutate(self, info, region, country, state, city, month, day, year, avg_temperature, latitude, longitude):
        temperature = Temperature(region=region, country=country, state=state, city=city, month=month, day=day, year=year, avg_temperature=avg_temperature, latitude=latitude, longitude=longitude)
        temperature.save()
        return CreateTemperature(temperature=temperature)
    

class UpdateTemperature(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        region = graphene.String(required=True)
        country = graphene.String(required=True)
        state = graphene.String(required=True)
        city = graphene.String(required=True)
        month = graphene.Int(required=True)
        day = graphene.Int(required=True)
        year = graphene.Int(required=True)
        avg_temperature = graphene.Float(required=True)
        latitude = graphene.Float(required=True)
        longitude = graphene.Float(required=True)
    
    temperature = graphene.Field(TemperatureType)

    def mutate(self, info, id, region=None, country=None, state=None, city=None, month=None, day=None, year=None, avg_temperature=None, latitude=None, longitude=None):
        try:
            temperature = Temperature.objects.get(id=id)
        except Temperature.DoesNotExist:
            raise Exception("Temperature not found")
        
        if region is not None:
            temperature.region = region
        if country is not None:
            temperature.country = country
        if state is not None:
            temperature.state = state
        if city is not None:
            temperature.city = city
        if month is not None:
            temperature.month = month
        if day is not None:
            temperature.day = day
        if year is not None:
            temperature.year = year
        if avg_temperature is not None:
            temperature.avg_temperature = avg_temperature
        if latitude is not None:
            temperature.latitude = latitude
        if longitude is not None:
            temperature.longitude = longitude
        temperature.save()
        return UpdateTemperature(temperature=temperature)
    

class DeleteTemperature(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            temperature = Temperature.objects.get(id=id)
        except Temperature.DoesNotExist:
            raise Exception("Temperature not found")
        
        temperature.delete()
        return DeleteTemperature(success=True)
    

class Query(graphene.ObjectType):
    all_temperatures = graphene.List(TemperatureType)

    def resolve_all_temperatures(self, info):
        return Temperature.objects.all()
    

class Mutation(graphene.ObjectType):
    create_temperature = CreateTemperature.Field()
    update_temperature = UpdateTemperature.Field()
    delete_temperature = DeleteTemperature.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)