from django.db import models
from django.contrib.auth.models import User
from datetime import datetime



class Solar_Config(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    time_zone1 = models.CharField(max_length=300)
    time_zone2 = models.CharField(max_length=300)


class Solar_Forecast(models.Model):
    time = models.DateTimeField()
    p_mp = models.FloatField()


class Battery_Config_Data(models.Model):
    time0 = models.DateTimeField(default=datetime.now, blank=True)
    initial_soc = models.FloatField()
    capacity = models.FloatField()


class LoadData(models.Model):
    date = models.DateField()
    temp = models.FloatField()