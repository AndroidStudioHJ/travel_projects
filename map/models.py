from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

 
# Create your models here.
class TravelPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    location_name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return f"{self.title} - {self.location_name}"
