import datetime
import pandas as pd
import solcast

latitude = 32.2
longitude = 110.9
tz = 'US/Arizona'
class Solar:
    def __init__(self,latitude,longitude,tz):
        self.latitude = latitude
        self.longitude = longitude
        self.tz = tz

    def solar_model(self):
        print(self.longitude)
        print(self.tz)
        pv_power_resp = solcast.get_pv_power_forecasts(self.latitude, self.longitude, capacity=2000, tilt=23,
                                                       azimuth=0,
                                                       api_key='xS2FpUCV7PHnWap-1ktf3Ktk1O1Z17k4')
        df = pd.DataFrame(pv_power_resp.forecasts, columns=['period', 'period_end', 'pv_estimate'])
        df.drop('period', axis=1, inplace=True)
        df['period_end'] = pd.to_datetime(df['period_end'])
        df['period_end'] = df['period_end'].dt.tz_convert(self.tz)
        df.set_index('period_end', inplace=True)
        df = df.resample('5min').interpolate()
        df.reset_index(inplace=True)
        #print(df)
        return df


def to_json(df):
    d = [dict([(colname, row[i]) for i, colname in enumerate(df.columns)]) for row in df.values]
    return d


#
# if __name__ == '__main__':
#     latitude = 32.2
#     longitude = 110.9
#     tz = 'US/Arizona'
#     pv1 = Solar(latitude, longitude, tz)
#     load = pv1.solar_model()
#     load.drop(['i_sc','v_mp','i_x','i_xx','i_mp','v_oc'], axis = 1, inplace  = True)
#     load.index.name = 'time'
#     load = load.reset_index(drop = False)
#     #load = load.to_json(orient='records', lines=True)
#     print(to_json(load))

