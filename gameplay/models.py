from django.db import models
from django.contrib.auth.models import User
from datetime import datetime



class Solar_Config(models.Model):
    latitude = models.CharField(max_length= 10)
    longitude = models.CharField(max_length= 10)
    time_zone1 = models.CharField(max_length=300)
    time_zone2 = models.CharField(max_length=300)


class Solar_Forecast(models.Model):
    time = models.DateTimeField()
    p_mp = models.FloatField()
    time_zone = models.CharField(max_length=100)


class Battery_Config_Data(models.Model):
    time0 = models.DateTimeField(default=datetime.utcnow(), blank=True)
    initial_soc = models.FloatField()
    capacity = models.FloatField()


class LoadData(models.Model):
    date = models.DateField()
    temp = models.FloatField()

class Energy(models.Model):
    energy = models.FloatField()
    energy_dsm = models.FloatField()