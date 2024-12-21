from django.db import models

# Create your models here.
class Temperature(models.Model):
    Region = models.CharField(max_length=255)
    Country_id = models.ForeignKey(
        'Country',
        on_delete=models.CASCADE,
        db_column='Country_id'
    )
    State = models.CharField(max_length=255)
    City = models.CharField(max_length=255)
    Month = models.IntegerField()
    Day = models.IntegerField()
    Year = models.IntegerField()
    AvgTemperature = models.FloatField()
    Latitude = models.FloatField()
    Longitude = models.FloatField()

    class Meta:
        db_table = "data"

    def __str__(self):
        return f"{self.Region}, {self.Country_id}, {self.State}, {self.City}, {self.Month}, {self.Day}, {self.Year}, {self.AvgTemperature}, {self.Latitude}, {self.Longitude}"
    

class Country(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "countries"

    def __str__(self):
        return self.name