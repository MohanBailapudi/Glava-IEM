from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect,HttpResponse
from .forms import Solar_Form, Battery_Form
from .models import Solar_Config, Solar_Forecast, Battery_Config_Data, LoadData
from django.urls import reverse
import json, logging
from tictactoe.views import solar


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
            #json_data = HttpResponse('solar_url', kwargs={'latitude': latitude,'longitude':longitude, 'time_zone1': time_zone1, 'time_zone2': time_zone2})
            data = json.loads(json_data)
            Solar_Forecast.objects.all().delete()
            for i in data:
                time = i.get('time', None)
                p_mp = i.get('p_mp', None)
                com = Solar_Forecast()
                com.time = time
                com.p_mp = p_mp
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
    return HttpResponseRedirect(reverse("upload_csv"))



