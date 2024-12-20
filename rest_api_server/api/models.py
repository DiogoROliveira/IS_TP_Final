from django.db import models

# Create your models here.
class Temperature(models.Model):
    region = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    month = models.IntegerField()
    day = models.IntegerField()
    year = models.IntegerField()
    avg_temperature = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.region}, {self.country}, {self.state}, {self.city}, {self.month}, {self.day}, {self.year}, {self.avg_temperature}, {self.latitude}, {self.longitude}"