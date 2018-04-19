"""tictactoe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from tictactoe.views import welcome, solar, Battery
from gameplay.views import get_solar_data, get_battery_data, upload_csv, start_iem, iem_started, test

urlpatterns = [
    path('admin/', admin.site.urls),
    path('welcome',welcome),
    url(r'solar/(?P<latitude>.*)/(?P<longitude>.*)/(?P<time_zone1>.*)/(?P<time_zone2>.*)/', solar, name= 'solar_url'),
    url(r'battery/(?P<initila_soc>.*)/(?P<capacity>.*)/(?P<period>.*)/(?P<mode>.*)/', Battery, name= 'battery_url'),
    url(r'solarform/', get_solar_data),
    url(r'batteryform/', get_battery_data),
    url(r'upload/csv/', upload_csv, name='upload_csv'),
    url(r'startiem/', start_iem, name='start_iem'),
    url(r'iemstarted/', iem_started, name='iem_started'),
    url(r'test/', test, name='test'),

]
