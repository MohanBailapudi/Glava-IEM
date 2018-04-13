import datetime
import inspect
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pvlib import solarposition,irradiance,atmosphere,pvsystem
from pvlib.forecast import GFS, NAM, NDFD, RAP, HRRR
import json as json

latitude = 32.2
longitude = 110.9
tz = 'US/Arizona'
class Solar:
    def __init__(self,latitude,longitude,tz):
        self.latitude = latitude
        self.longitude = longitude
        self.tz = tz

    def solar_model(self):
        surface_tilt = 30
        surface_azimuth = 180  # pvlib uses 0=North, 90=East, 180=South, 270=West convention
        albedo = 0.2

        start = pd.Timestamp(datetime.date.today(), tz=self.tz)  # today's date
        end = start + pd.Timedelta(days=7)  # 7 days from today

        fm = GFS()
        # fm = NAM()
        # fm = NDFD()
        # fm = RAP()
        # fm = HRRR()

        forecast_data = fm.get_processed_data(self.latitude, - self.longitude, start, end)
        ghi = forecast_data['ghi']
        resampled_data = forecast_data.resample('5min').interpolate()  # retrieve time and location parameters
        time = forecast_data.index

        a_point = fm.location
        solpos = a_point.get_solarposition(time)
        dni_extra = irradiance.extraradiation(fm.time)
        airmass = atmosphere.relativeairmass(solpos['apparent_zenith'])
        poa_sky_diffuse = irradiance.haydavies(surface_tilt, surface_azimuth,
                                               forecast_data['dhi'], forecast_data['dni'], dni_extra,
                                               solpos['apparent_zenith'], solpos['azimuth'])
        poa_ground_diffuse = irradiance.grounddiffuse(surface_tilt, ghi, albedo=albedo)
        aoi = irradiance.aoi(surface_tilt, surface_azimuth, solpos['apparent_zenith'], solpos['azimuth'])
        poa_irrad = irradiance.globalinplane(aoi, forecast_data['dni'], poa_sky_diffuse, poa_ground_diffuse)
        temperature = forecast_data['temp_air']
        wnd_spd = forecast_data['wind_speed']
        pvtemps = pvsystem.sapm_celltemp(poa_irrad['poa_global'], wnd_spd, temperature)
        sandia_modules = pvsystem.retrieve_sam('SandiaMod')
        sandia_module = sandia_modules.Canadian_Solar_CS5P_220M___2009_
        effective_irradiance = pvsystem.sapm_effective_irradiance(poa_irrad.poa_direct, poa_irrad.poa_diffuse,
                                                                  airmass, aoi, sandia_module)
        sapm_out = pvsystem.sapm(effective_irradiance, pvtemps['temp_cell'], sandia_module)
        return sapm_out


def to_json(df):
    d = [dict([(colname, row[i]) for i, colname in enumerate(df.columns)]) for row in df.values]
    return d



if __name__ == '__main__':
    latitude = 32.2
    longitude = 110.9
    tz = 'US/Arizona'
    pv1 = Solar(latitude, longitude, tz)
    load = pv1.solar_model()
    load.drop(['i_sc','v_mp','i_x','i_xx','i_mp','v_oc'], axis = 1, inplace  = True)
    load.index.name = 'time'
    load = load.reset_index(drop = False)
    #load = load.to_json(orient='records', lines=True)
    print(to_json(load))
