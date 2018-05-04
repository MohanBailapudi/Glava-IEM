from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponseRedirect,HttpResponse, JsonResponse
from .forms import Solar_Form, Battery_Form
from .models import Solar_Config, Solar_Forecast, Battery_Config_Data, LoadData, Energy
from django.urls import reverse
import json, logging, requests, threading
from _thread import start_new_thread
from django.utils import timezone
#from tictactoe.views import solar
from django.db import transaction
from pandas import Timestamp
from django.template.response import TemplateResponse
from datetime import datetime
from simulators.battery_simulator import Battery
from test import batter_degradaion_cost
from django.views.decorators.csrf import csrf_exempt
from influxdb import InfluxDBClient

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

@csrf_exempt
def two_froms(request):
    if request.method == 'POST':
        client = InfluxDBClient('52.14.130.182', 8086, 'TestSeries')
        client.delete_series(database='TestSeries', measurement='glava_iem_savings_algorithm')
        # create a form instance and populate it with data from the request:
        #form1 = Solar_Form(data=request.POST)
        # check whether it's valid:
        #if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
        #data = json.loads(request.body)
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']
        time_zone1 = request.POST['time_zone']
        # time_zone2 = request.POST['time_zone2']
        # solar_data = Solar_Config(latitude = latitude, longitude = longtude, time_zone = time_zone)
        # solar_data.save()
        #json_data = solar(request, latitude, longitude, time_zone1).content
        # print(json_data)
        # json_data = HttpResponse('solar_url', kwargs={'latitude': latitude,'longitude':longitude, 'time_zone1': time_zone1, 'time_zone2': time_zone2})
        #data = json.loads(json_data)
        Solar_Forecast.objects.all().delete()
        # id = 0
        # with transaction.atomic():
        #     for i in data:
        #         time = i.get('period_end', None)
        #         p_mp = i.get('pv_estimate', None)
        #         com = Solar_Forecast()
        #         com.time = time
        #         com.p_mp = p_mp
        #         com.time_zone = time_zone1
        #         id = id + 1
        #         com.id = id
        #         com.save()
        # form2 = Battery_Form(data=request.POST)
        Battery_Config_Data.objects.all().delete()
        Energy.objects.all().delete()
        initial_soc = request.POST['initial_soc']
        capacity = request.POST['capacity']
        com = Battery_Config_Data()
        com.initial_soc = initial_soc
        com.capacity = capacity
        com.save()
    else:
        print('failed')
    return HttpResponse('Hi')

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

def battery_cherge(soc, time0, capacity, p_dsm):

    while round(soc,2) <= 40.2:

        time_now1 = str(datetime.utcnow())[0:-7]
        time_now1 = datetime.strptime(time_now1, '%Y-%m-%d %H:%M:%S')
        dt = (time_now1 - time0).total_seconds() / 3600.0
        current_soc = Battery(soc, dt, 'C', capacity)
        current = p_dsm / 350
        current_soc.update_current(0, current)
        soc = current_soc.soc_cc()
        battery_cherge(soc, time0, capacity, p_dsm)
    bat_initial_data = Battery_Config_Data.objects.latest('id')
    time_now10 = datetime.utcnow()
    bat_initial_data.time0 = time_now10
    bat_initial_data.initial_soc = soc
    bat_initial_data.save()

@csrf_exempt
def iem_started(request):
    if request.method == 'GET':
        time_now = Timestamp(datetime.utcnow()).isoformat()[0:-10]
        time_now10 = datetime.utcnow()
        time_now1 = str(datetime.utcnow())[0:-7]
        time_now1 = datetime.strptime(time_now1, '%Y-%m-%d %H:%M:%S')
        #data = Solar_Forecast.objects.filter(time__gte=time_now)[:5]
        data = json.loads(requests.get("https://dzdtwfo3h4.execute-api.us-east-2.amazonaws.com/production/GlavaChannelDataReader").text)
        data = data['data'][0]
        pv_forecast = []
        global system_status, battery_status, grid_sharing, cost_with_algorithm, cost_if_grid_is_supplying, savings
        savings = 0
        system_status = ""
        battery_status = ""
        grid_sharing = ""
        p_bat_max = 1000
        # for i in data:
        #     pv_forecast.append(i.p_mp)
        pv_forecast.append(float(data['CH_03'])*3.5)
        bat_initial_data = Battery_Config_Data.objects.latest('id')
        load = (float(data['CH_07'])+float(data['CH_08']))*3.5
        # load = 700
        time0 = datetime.strptime(str(bat_initial_data.time0)[0:-13], '%Y-%m-%d %H:%M:%S')
        grid_status = 1
        c_utility = 20
        p_grid_max = 1000
        c_utility_min = 10
        soc_min = 20
        soc_mid = 40
        soc_max = 80
        p_dsm = 200
        if grid_status == 0:
            system_status = "Islanded Mode"
            if pv_forecast[0] != 0:
                p_bal = pv_forecast[0] - load
                initial_soc = bat_initial_data.initial_soc,4
                dt = (time_now1 - time0).total_seconds() / 3600.0
                capacity = bat_initial_data.capacity
                if p_bal > 0:
                    if initial_soc < soc_max:
                        if p_bal < p_bat_max:
                            current_soc = Battery(initial_soc, dt, 'C', capacity)
                            current_soc.update_current(0, 2)
                            soc = current_soc.soc_cc()
                            bat_initial_data.initial_soc = soc
                            bat_initial_data.time0 = time_now10
                            bat_initial_data.save()
                            battery_status = "Battery is Charging from excess PV"
                        else:
                            print("pv shedding")
                    else:
                        print("pv shedding")
                else:
                    if initial_soc >= soc_mid:
                        if p_bal < p_bat_max:
                            current_soc = Battery(initial_soc, dt, 'D', capacity)
                            current_soc.update_current(0, 2)
                            soc = current_soc.soc_cc()
                            bat_initial_data.initial_soc = soc
                            bat_initial_data.time0 = time_now10
                            bat_initial_data.save()
                            battery_status = "Battery is Discharging to meet the balance load"
                            savings1 = abs(p_bal) * dt / 1000
                            try:
                                com = Energy.objects.latest('id')
                                temp = com.energy
                                com.energy = savings1 + temp
                                com.energy_dsm = 0
                            except:
                                com = Energy()
                                com.energy = savings1
                                com.energy_dsm = 0
                            com.save()
                            c_bat = batter_degradaion_cost(soc, 1)
                            cost_with_algorithm = Energy.objects.latest('id').energy * (c_bat)
                            cost_if_grid_is_supplying = 0
                            savings = 0
                        else:
                            current_soc = Battery(initial_soc, dt, 'D', capacity)
                            ### Demand Side Management ###
                            current = p_bal - p_dsm / 350
                            current_soc.update_current(0, current)
                            soc = current_soc.soc_cc()
                            bat_initial_data.initial_soc = soc
                            bat_initial_data.time0 = time_now10
                            bat_initial_data.save()
                            battery_status = "Battery is Discharging to meet the load after DSM"
                            savings1 = abs(p_bal - p_dsm) * dt / 1000
                            try:
                                com = Energy.objects.latest('id')
                                temp = com.energy
                                com.energy = savings1 + temp
                                com.energy_dsm = 0
                            except:
                                com = Energy()
                                com.energy = savings1
                                com.energy_dsm = 0
                            com.save()
                            c_bat = batter_degradaion_cost(soc, 1)
                            cost_with_algorithm = Energy.objects.latest('id').energy * (c_bat)
                            cost_if_grid_is_supplying = 0
                            savings = 0
                    else:
                        if initial_soc > soc_min and initial_soc < soc_mid:
                            battery_status = "Battery Turned-off"
                            cost_with_algorithm = 0
                            cost_if_grid_is_supplying = 0
                            savings = 0

                        else:
                            if pv_forecast[0] > 0:
                                battery_status = "Battery Turned-off"
                                cost_with_algorithm = 0
                                cost_if_grid_is_supplying = 0
                                savings = 0
                            else:
                                #print("shutdown")
                                cost_with_algorithm = 0
                                cost_if_grid_is_supplying = 0
                                savings = 0
        ### Grid Connected ###
        else:
            system_status = "Connected to Grid"
            if pv_forecast[0] != 0:
                p_bal = pv_forecast[0] - load
                initial_soc = bat_initial_data.initial_soc
                dt = (time_now1 - time0).total_seconds() / 3600.0
                capacity = bat_initial_data.capacity
                if p_bal >= 0:
                    if initial_soc < soc_max:
                        current_soc = Battery(initial_soc, dt, 'C', capacity)
                        current = p_bal / 350
                        current_soc.update_current(0, current)
                        soc = current_soc.soc_cc()
                        bat_initial_data.initial_soc = soc
                        bat_initial_data.time0 = time_now10
                        bat_initial_data.save()
                        battery_status = "Battery charging from excess PV"
                        grid_sharing = "Sharing Zero load"
                        cost_with_algorithm = 0
                        cost_if_grid_is_supplying = 0
                        savings = 0
                    else:
                        battery_status = "Battery Full disconnecting battery from charging"
                        grid_sharing = "Sharing Zero load"
                        cost_with_algorithm = 0
                        cost_if_grid_is_supplying = 0
                        savings = 0
                        #print("pv shedding")
                else:
                    c_bat = batter_degradaion_cost(initial_soc, 1)
                    if c_bat > c_utility:
                        if p_bal < p_grid_max:
                            if c_utility == c_utility_min:
                                if initial_soc < soc_max:
                                    current_soc = Battery(initial_soc, dt, 'C', capacity)
                                    current = p_grid_max - p_bal / 350
                                    current_soc.update_current(0, current)
                                    soc = current_soc.soc_cc()
                                    bat_initial_data.initial_soc = soc
                                    bat_initial_data.time0 = time_now10
                                    bat_initial_data.save()
                                    battery_status = "Battery Charging from grid at minimum price"
                                    grid_sharing = "Charging the battery and supplying the load at minimum unit price"
                                    savings1 = abs(p_bal + p_grid_max - p_bal) * dt / 1000
                                    try:
                                        com = Energy.objects.latest('id')
                                        temp = com.energy
                                        com.energy = savings1 + temp
                                        com.energy_dsm = 0
                                    except:
                                        com = Energy()
                                        com.energy = savings1
                                        com.energy_dsm = 0
                                    com.save()
                                    c_bat = batter_degradaion_cost(soc, 1)
                                    cost_with_algorithm = Energy.objects.latest('id').energy * (c_utility_min)
                                    cost_if_grid_is_supplying = Energy.objects.latest('id').energy * (c_utility_min)
                                    savings = 0
                                else:
                                    battery_status = "Battery Full disconnecting it"
                                    grid_sharing = "Supplying the load at minimum unit price"
                                    savings1 = abs(p_bal) * dt / 1000
                                    try:
                                        com = Energy.objects.latest('id')
                                        temp = com.energy
                                        com.energy = savings1 + temp
                                    except:
                                        com = Energy()
                                        com.energy = savings1
                                    com.save()
                                    cost_with_algorithm = Energy.objects.latest('id').energy * (c_utility_min)
                                    cost_if_grid_is_supplying = Energy.objects.latest('id').energy * (c_utility_min)
                                    savings = 0
                            else:
                                battery_status = "Battery is idle"
                                grid_sharing = "Supplying the load at minimum unit price"
                                savings1 = abs(p_bal) * dt / 1000
                                try:
                                    com = Energy.objects.latest('id')
                                    temp = com.energy
                                    com.energy = savings1 + temp
                                except:
                                    com = Energy()
                                    com.energy = savings1
                                com.save()
                                cost_with_algorithm = Energy.objects.latest('id').energy * (c_utility_min)
                                cost_if_grid_is_supplying = Energy.objects.latest('id').energy * (c_utility_min)
                                savings = 0

                    elif soc_mid < round(initial_soc,4):
                        #print("disconnect the grid")
                        if p_bal < p_bat_max:
                            current_soc = Battery(initial_soc, dt, 'D', capacity)
                            current = p_bal / 350
                            current_soc.update_current(0, current)
                            soc = current_soc.soc_cc()
                            bat_initial_data.initial_soc = soc
                            bat_initial_data.time0 = time_now10
                            bat_initial_data.save()
                            battery_status = "Battery Discharging is cheap to supply the load"
                            grid_sharing = "Sharing Zero load"
                            savings1 = abs(p_bal) * dt / 1000
                            try:
                                com = Energy.objects.latest('id')
                                temp = com.energy
                                com.energy = savings1 + temp
                                com.energy_dsm = 0
                            except:
                                com = Energy()
                                com.energy = savings1
                                com.energy_dsm = 0
                            com.save()
                            cost_with_algorithm = Energy.objects.latest('id').energy * (c_bat)
                            cost_if_grid_is_supplying = Energy.objects.latest('id').energy * (c_utility)
                            savings = cost_if_grid_is_supplying - cost_with_algorithm
                        else:
                            current_soc = Battery(initial_soc, dt, 'D', capacity)
                            ### Demand Side Management ###
                            current = p_bal - p_dsm / 350
                            current_soc.update_current(0, current)
                            soc = current_soc.soc_cc()
                            bat_initial_data.initial_soc = soc
                            bat_initial_data.time0 = time_now10
                            bat_initial_data.save()
                            battery_status = "Battery available capaity is less than the load, DSM id done and balance is supplied by battery"
                            savings1 = abs(p_bal-p_dsm) * dt / 1000
                            cost_dsm = p_dsm*dt/1000
                            try:
                                com = Energy.objects.latest('id')
                                temp = com.energy
                                temp1 = com.energy_dsm
                                com.energy = savings1 + temp
                                com.energy_dsm = temp1 + cost_dsm
                            except:
                                com = Energy()
                                com.energy = savings1
                                com.energy_dsm = cost_dsm
                            com.save()
                            cost_with_algorithm = Energy.objects.latest('id').energy * (c_bat) + Energy.objects.latest('id').energy_dsm*c_utility
                            cost_if_grid_is_supplying = (Energy.objects.latest('id').energy + Energy.objects.latest('id').energy_dsm)*c_utility
                            savings = cost_if_grid_is_supplying - cost_with_algorithm
                    elif round(initial_soc,4) == soc_mid:
                        battery_status = "Battery reached minimum limit"
                        grid_sharing = "Supplying the load at ToU price after DSM"
                        soc = initial_soc
                        savings1 = abs(p_bal - p_dsm) * dt / 1000
                        cost_dsm = p_dsm * dt / 1000
                        try:
                            com = Energy.objects.latest('id')
                            temp = com.energy
                            temp1 = com.energy_dsm
                            com.energy = savings1 + temp
                            com.energy_dsm = temp1 + cost_dsm
                        except:
                            com = Energy()
                            com.energy = savings1
                            com.energy_dsm = cost_dsm
                        com.save()
                        cost_with_algorithm = Energy.objects.latest('id').energy * c_utility
                        cost_if_grid_is_supplying = (Energy.objects.latest('id').energy + Energy.objects.latest('id').energy_dsm) * c_utility
                        savings = cost_if_grid_is_supplying - cost_with_algorithm
                        start_new_thread(battery_cherge, (initial_soc, time0, capacity, p_dsm,))

                    else:
                        # t1 = threading.Thread(target=battery_cherge, args=(initial_soc, time0, capacity, p_dsm,))
                        # t1.start()
                        # t1.join()
                        start_new_thread(battery_cherge, (initial_soc, time0, capacity, p_dsm,))
                        battery_status = "Battery below minimum limit"
                        grid_sharing = "Supplying the load at ToU price after DSM"
                        savings1 = abs(p_bal - p_dsm) * dt / 1000
                        cost_dsm = p_dsm * dt / 1000
                        try:
                            com = Energy.objects.latest('id')
                            temp = com.energy
                            temp1 = com.energy_dsm
                            com.energy = savings1 + temp
                            com.energy_dsm = temp1 + cost_dsm
                        except:
                            com = Energy()
                            com.energy = savings1
                            com.energy_dsm = cost_dsm
                        com.save()
                        cost_with_algorithm = Energy.objects.latest('id').energy * c_utility
                        cost_if_grid_is_supplying = (Energy.objects.latest('id').energy + Energy.objects.latest(
                            'id').energy_dsm) * c_utility
                        savings = cost_if_grid_is_supplying - cost_with_algorithm

        battery_data = Battery_Config_Data.objects.latest('id')
        pv_data = pv_forecast[0]
        payload = {'system_status': system_status, 'battery_status': battery_status, 'grid_status': grid_sharing,
                   'load': load, 'battery_soc': round(battery_data.initial_soc,4), 'pv_forecast': round(pv_data,4), 'savings': round(savings,4), 'cost_if_grid_is_supplying': round(cost_if_grid_is_supplying,4), 'cost_with_algorithm': round(cost_with_algorithm,4) }
        # url = "http://172.16.18.148:3000/send_notification"
        # r = requests.post(url, data=json.loads(json.dumps(payload)))
        # print(r.status_code)
        #payload1 = {'CostWithExistingSystem': round(cost_if_grid_is_supplying,4), 'CostWithAlgorithm': round(cost_with_algorithm,4),'Savings': round(savings,4)}
        payload1 = {'data':{'CostWithExistingSystem': int(cost_if_grid_is_supplying), 'CostWithAlgorithm': int(cost_with_algorithm),'Savings': int(savings)}}
        #url = "https://jtxskf9600.execute-api.us-east-2.amazonaws.com/production/glava-iem-cost-saving-alogorithm"
        headers = {"content-type": "application/json"}
        url = "https://3mz01xr037.execute-api.us-east-1.amazonaws.com/test/test_idb"
        r = requests.post(url, data=json.dumps(payload1), headers = headers)
        print("lambda status:", r.status_code)
        print(r.text)
        return JsonResponse(payload, safe=False)
    #return render(request,'displaydata.html', {'battery_data':battery_data, 'pv_data':pv_data, 'load':load, 'system_status':system_status, 'battery_status':battery_status, 'grid_sharing':grid_sharing})


@csrf_exempt
def test(request):
    if request.method == 'GET':
        latitude =  json.loads(request.body)
        #return render(request,'two_forms.html',{'latitude':latitude})
    return HttpResponse("Hi")