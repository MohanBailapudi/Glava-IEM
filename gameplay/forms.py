from django import forms




class Solar_Form(forms.Form):
    latitude = forms.FloatField(label='latitude')
    longitude = forms.FloatField(label='longitude')
    time_zone1 = forms.CharField(label='time_zone1', max_length=100)
    time_zone2 = forms.CharField(label='time_zone2', max_length=100)

class Battery_Form(forms.Form):
    initial_soc = forms.FloatField(label = 'initial_soc')
    capacity = forms.FloatField(label = 'capacity')


