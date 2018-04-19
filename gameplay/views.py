from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponseRedirect,HttpResponse, JsonResponse
from .forms import Solar_Form, Battery_Form
from .models import Solar_Config, Solar_Forecast, Battery_Config_Data, LoadData
from django.urls import reverse
import json, logging
from django.utils import timezone
from tictactoe.views import solar
from django.db import transaction
from pandas import Timestamp
from django.template.response import TemplateResponse
from datetime import datetime
from simulators.battery_simulator import Battery

def get_solar_data(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = Solar_Form(data=request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
            time_zone1 = request.POST['time_zone1']
            time_zone2 = request.POST['time_zone2']
            # solar_data = Solar_Config(latitude = latitude, longitude = longtude, time_zone = time_zone)
            # solar_data.save()
            json_data = solar(request,latitude,longitude,time_zone1,time_zone2).content
            #print(json_data)
            #json_data = HttpResponse('solar_url', kwargs={'latitude': latitude,'longitude':longitude, 'time_zone1': time_zone1, 'time_zone2': time_zone2})
            data = json.loads(json_data)
            Solar_Forecast.objects.all().delete()
            id = 0
            with transaction.atomic():
                for i in data:
                    time = i.get('period_end', None)
                    p_mp = i.get('pv_estimate', None)
                    com = Solar_Forecast()
                    com.time = time
                    com.p_mp = p_mp
                    com.time_zone = time_zone1+"/"+time_zone2
                    id = id+1
                    com.id = id
                    com.save()

            return HttpResponseRedirect('/batteryform/')
            #return render(request, 'solar.html', {'form': form})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = Solar_Form()

    return render(request, 'solar.html', {'form': form})


def get_battery_data(request):

    if request.method == 'POST':
        form = Battery_Form(data=request.POST)
        Battery_Config_Data.objects.all().delete()
        if form.is_valid:
            initial_soc = request.POST['initial_soc']
            capacity = request.POST['capacity']
            com = Battery_Config_Data()
            com.initial_soc = initial_soc
            com.capacity = capacity
            com.save()
            return HttpResponseRedirect('/upload/csv/')

    else:
        form = Battery_Form()

    return render(request, 'battery.html', {'form': form})


def upload_csv(request):
    data = {}
    if "GET" == request.method:
        return render(request, "csvuplaod.html", data)
    # if not GET, then proceed
    try:
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not CSV type')
            return HttpResponseRedirect(reverse("upload_csv"))
        # if file is too large, return
        if csv_file.multiple_chunks():
            messages.error(request, "Uploaded file is too big (%.2f MB)." % (csv_file.size / (1000 * 1000),))
            return HttpResponseRedirect(reverse("upload_csv"))

        file_data = csv_file.read().decode("utf-8")

        lines = file_data.split("\n")
        # loop over the lines and save them in db. If error , store as string and then display
        for line in lines:
            fields = line.split(",")
            try:
                com = LoadData()
                com.date = fields[0]
                com.temp = fields[1]
                com.save()
            except Exception as e:
                logging.getLogger("error_logger").error(repr(e))
                pass
    except Exception as e:
        logging.getLogger("error_logger").error("Unable to upload file. " + repr(e))
    return HttpResponseRedirect(reverse("start_iem"))


def start_iem(request):
    data = {}
    if "GET" == request.method:
        return render(request,'start_iem.html', data)
    return HttpResponseRedirect(reverse("iem_started"))


def iem_started(request):
    time_now = Timestamp(datetime.utcnow()).isoformat()[0:-16]
    time_now10 = datetime.utcnow()
    time_now1 = str(datetime.utcnow())[0:-7]
    time_now1 = datetime.strptime(time_now1, '%Y-%m-%d %H:%M:%S')
    data = Solar_Forecast.objects.filter(time__gte = time_now)[:5]
    pv_forecast = []
    for i in data:
        pv_forecast.append(i.p_mp)
    bat_initial_data = Battery_Config_Data.objects.latest('id')
    load = 300
    time0 = datetime.strptime(str(bat_initial_data.time0)[0:-13],'%Y-%m-%d %H:%M:%S')
    if pv_forecast[0] > 0:
        p_bal = pv_forecast[0] - load
        initial_soc = bat_initial_data.initial_soc
        dt = (time_now1 - time0).total_seconds() / 3600.0
        capacity = bat_initial_data.capacity
        if p_bal > 0:
            current_soc = Battery(initial_soc,dt,'C',capacity)
            current_soc.update_current(0,2)
            soc = current_soc.soc_cc()
            bat_initial_data.initial_soc = soc
            bat_initial_data.time0 = time_now10
            bat_initial_data.save()
        else:
            current_soc = Battery(initial_soc, dt, 'D', capacity)

        print(soc)

    return render(request,'displaydata.html', {'data':data, 'data1':bat_initial_data})

def test(request):
    if request.method == 'GET':
        return JsonResponse({'hello':'Hi Teja999'}, safe=False)