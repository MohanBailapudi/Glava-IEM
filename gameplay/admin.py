from django.contrib import admin
from .models import Solar_Config, Solar_Forecast, Battery_Config_Data, LoadData

admin.site.register(Solar_Config)
admin.site.register(Solar_Forecast)
admin.site.register(Battery_Config_Data)
admin.site.register(LoadData)