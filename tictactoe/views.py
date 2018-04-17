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
    pv1 = Solar(float(latitude),float(longitude),tz)
    load = pv1.solar_model()
    # load.drop('period', axis=1, inplace=True)
    # load['period_end'] = pd.to_datetime(load['period_end'])
    # load['period_end'] = load['period_end'].dt.tz_localize('UTC').dt.tz_convert('Europe/Stockholm').dt.tz_localize(None)
    # load.set_index('period_end', inplace=True)
    # load = load.resample('5min')
    # load.reset_index(inplace=True)
    load = to_json(load)
    return JsonResponse(load, safe=False)

#def Battery(request,initila_soc,capacity,period,mode):
