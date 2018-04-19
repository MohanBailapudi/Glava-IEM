from django.http import HttpResponse, JsonResponse
from simulators.solar_simulator import Solar,to_json
from simulators.battery_simulator import Battery
from django.core import serializers
from datetime import datetime
import pandas as pd



def welcome(request):
    return HttpResponse("Hello World!")

def solar(request,latitude,longitude,time_zone1, time_zone2):
    tz = str(time_zone1+"/"+time_zone2)
    if 'N' in latitude and 'E' in longitude:
        pv1 = Solar(float(latitude[0:-1]),float(longitude[0:-1]),tz)
        load = pv1.solar_model()
    elif 'N' in latitude and 'W' in longitude:
        pv1 = Solar(float(latitude[0:-1]), -float(longitude[0:-1]), tz)
        load = pv1.solar_model()
        print('pass')
    elif 'S' in latitude and 'W' in longitude:
        pv1 = Solar(-float(latitude[0:-1]), -float(longitude[0:-1]), tz)
        load = pv1.solar_model()
    elif 'S' in latitude and 'E' in longitude:
        pv1 = Solar(-float(latitude[0:-1]), float(longitude[0:-1]), tz)
        load = pv1.solar_model()
    # load.drop('period', axis=1, inplace=True)
    # load['period_end'] = pd.to_datetime(load['period_end'])
    # load['period_end'] = load['period_end'].dt.tz_localize('UTC').dt.tz_convert('Europe/Stockholm').dt.tz_localize(None)
    # load.set_index('period_end', inplace=True)
    # load = load.resample('5min').interpolate()
    # load.reset_index(inplace=True)
    #print(load)
    load = to_json(load)
    #print(load)
    return JsonResponse(load, safe=False)

#def Battery(request,initila_soc,capacity,period,mode):
