import graphene
from graphene_django import DjangoObjectType
from .models import Temperature, Country

class CountryType(DjangoObjectType):
    class Meta:
        model = Country
        fields = "__all__"

class TemperatureType(DjangoObjectType):
    class Meta:
        model = Temperature
        fields = "__all__"

class CityType(graphene.ObjectType):
    nome = graphene.String()
    latitude = graphene.Float()
    longitude = graphene.Float()
    id = graphene.ID()

class CreateCountry(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
    
    country = graphene.Field(CountryType)

    def mutate(self, info, name):
        country = Country(name=name)
        country.save()
        return CreateCountry(country=country)

class CreateTemperature(graphene.Mutation):
    class Arguments:
        Region = graphene.String(required=True)
        Country_id = graphene.Int(required=True) 
        State = graphene.String(required=True)
        City = graphene.String(required=True)
        Month = graphene.Int(required=True)
        Day = graphene.Int(required=True)
        Year = graphene.Int(required=True)
        AvgTemperature = graphene.Float(required=True)
        Latitude = graphene.Float(required=True)
        Longitude = graphene.Float(required=True)
    
    temperature = graphene.Field(TemperatureType)

    def mutate(self, info, Region, Country_id, State, City, Month, Day, Year, AvgTemperature, Latitude, Longitude):
        try:
            country = Country.objects.get(id=Country_id)
            temperature = Temperature(
                Region=Region,
                Country_id=country,
                State=State,
                City=City,
                Month=Month,
                Day=Day,
                Year=Year,
                AvgTemperature=AvgTemperature,
                Latitude=Latitude,
                Longitude=Longitude
            )
            temperature.save()
            return CreateTemperature(temperature=temperature)
        except Country.DoesNotExist:
            raise Exception("Country not found")

class UpdateTemperature(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        Region = graphene.String()
        Country_id = graphene.Int()
        State = graphene.String()
        City = graphene.String()
        Month = graphene.Int()
        Day = graphene.Int()
        Year = graphene.Int()
        AvgTemperature = graphene.Float()
        Latitude = graphene.Float()
        Longitude = graphene.Float()
    
    temperature = graphene.Field(TemperatureType)

    def mutate(self, info, id, **kwargs):
        try:
            temperature = Temperature.objects.get(id=id)
            
            for key, value in kwargs.items():
                if value is not None:
                    if key == 'country_id':
                        country = Country.objects.get(id=value)
                        setattr(temperature, 'country_id', country)
                    else:
                        setattr(temperature, key, value)
            
            temperature.save()
            return UpdateTemperature(temperature=temperature)
        except Temperature.DoesNotExist:
            raise Exception("Temperature not found")
        except Country.DoesNotExist:
            raise Exception("Country not found")

class DeleteTemperature(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    temperature = graphene.Field(TemperatureType)

    def mutate(self, info, id):
        try:
            temperature = Temperature.objects.get(id=id)
            temperature.delete()
            return DeleteTemperature(temperature=temperature)
        except Temperature.DoesNotExist:
            raise Exception("Temperature not found")

class Query(graphene.ObjectType):
    all_temperatures = graphene.List(TemperatureType)
    all_countries = graphene.List(CountryType)
    temperature_by_id = graphene.Field(TemperatureType, id=graphene.Int(required=True))
    temperatures_by_country = graphene.List(TemperatureType, country_id=graphene.Int(required=True))
    cities = graphene.List(CityType, nome=graphene.String())

    def resolve_all_temperatures(self, info):
        return Temperature.objects.all()

    def resolve_all_countries(self, info):
        return Country.objects.all()

    def resolve_temperature_by_id(self, info, id):
        try:
            return Temperature.objects.get(id=id)
        except Temperature.DoesNotExist:
            return None

    def resolve_temperatures_by_country(self, info, country_id):
        return Temperature.objects.filter(country_id=country_id)
    
    def resolve_cities(self, info, nome=None):
        query = Temperature.objects.values('City', 'Latitude', 'Longitude', 'id').distinct()
        if nome:
            query = query.filter(City__icontains=nome)
        return [
            CityType(
                nome=city['City'],
                latitude=city['Latitude'],
                longitude=city['Longitude'],
                id=city['id']
            ) for city in query
        ]

class Mutation(graphene.ObjectType):
    create_temperature = CreateTemperature.Field()
    create_country = CreateCountry.Field()
    update_temperature = UpdateTemperature.Field()
    delete_temperature = DeleteTemperature.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)