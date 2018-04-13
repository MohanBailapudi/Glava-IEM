from django.http import HttpResponse, JsonResponse
from simulators.solar_simulator import Solar,to_json
from simulators.battery_simulator import Battery
from django.core import serializers



def welcome(request):
    return HttpResponse("Hello World!")

def solar(request,latitude,longitude,time_zone1, time_zone2):
    tz = str(time_zone1+"/"+time_zone2)
    pv1 = Solar(float(latitude),float(longitude),tz)
    load = pv1.solar_model()
    load.drop(['i_sc', 'v_mp', 'i_x', 'i_xx', 'i_mp', 'v_oc'], axis=1, inplace=True)
    load.index.name = 'time'
    load = load.reset_index(drop=False)
    load = to_json(load)
    return JsonResponse(load, safe=False)

#def Battery(request,initila_soc,capacity,period,mode):
