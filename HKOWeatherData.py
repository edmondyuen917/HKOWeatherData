# test git add 16:24
# test git add 16:28 on notebook
# test git add 16:29 on notebook


'''
API to retrieve daily mean temperature by specified year
https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=CLMTEMP&lang=en&rformat=csv&station=CCH&year=2024


API to retrieve current temperature and RH
https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en

'''

import requests
import time
import os
import sys
# import datetime
from datetime import datetime, timezone, timedelta
from csv import reader
import pytz

# print('Number of arguments:', len(sys.argv), 'arguments.')
# print('Argument List:', str(sys.argv))



api_url = 'https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en'
temp_file_out = "temperature.csv"
rh_file_out = "rh.csv"

# init last time from temperature.csv and rh.csv
def init_last_time():
    if not os.path.exists(temp_file_out):
        temp_last_update_time = datetime.fromisoformat('2024-01-01T10:11:00+08:00')
    else:
        with open(temp_file_out, "r") as tempfile:
            lines = tempfile.readlines()
            line = lines [len(lines)-1].split(",")
            format = '%m/%d/%Y %H:%M:%S'
            dt = datetime.strptime(line[0], format) 
            tz = pytz.timezone('Asia/Hong_Kong')
            temp_last_update_time = tz.localize(dt, is_dst=None)
            print(f'init temp_last_update_time: {temp_last_update_time}')

    if not os.path.exists(rh_file_out):
        rh_last_update_time = datetime.fromisoformat('2024-01-01T10:11:00+08:00')
    else:
        with open(rh_file_out, "r") as rhfile:
            lines = rhfile.readlines()
            line = lines [len(lines)-1].split(",")
            format = '%m/%d/%Y %H:%M:%S'
            dt = datetime.strptime(line[0], format) 
            tz = pytz.timezone('Asia/Hong_Kong')
            rh_last_update_time = tz.localize(dt, is_dst=None)
            print(f'init rh_last_update_time: {rh_last_update_time}')            

    return temp_last_update_time, rh_last_update_time

def save_temperature_rh(temp_last_update_time,rh_last_update_time):
    # print(f'temp_last_update_time: {temp_last_update_time},rh_last_update_time: {rh_last_update_time} ')
    try:
        with open(temp_file_out, "a") as tempfile, open(rh_file_out, "a") as rhfile:
            response = requests.get(api_url)
            datas = response.json()
            updateTime = datas['updateTime']
            dt = datetime.fromisoformat(updateTime)
            # print(dt)
            if (dt > temp_last_update_time):
                print('record temperature')
                temp_last_update_time = dt
                dt_str = dt.strftime("%m/%d/%Y %H:%M:%S")
                temp_datas = datas['temperature']['data']
                for temp_data in temp_datas:
                    # print(temp_data)
                    place = temp_data['place']
                    temperature = temp_data['value']
                    s = dt_str + ',' + place + ',' + str(temperature)
                    # print(s)
                    print(s, file=tempfile)

            rh_updateTime = datas['humidity']['recordTime']
            rh_dt = datetime.fromisoformat(rh_updateTime)
            if (rh_dt > rh_last_update_time):
                print('record RH')
                rh_last_update_time = rh_dt
                dt_str = rh_dt.strftime("%m/%d/%Y %H:%M:%S")
                rh_datas = datas['humidity']['data']
                for rh_data in rh_datas:
                    # print(temp_data)
                    place = rh_data['place']
                    rh = rh_data['value']
                    s = dt_str + ',' + place + ',' + str(rh)
                    # print(s)
                    print(s, file=rhfile)
            return temp_last_update_time, rh_last_update_time
    except:
        print('error!')
        return 0,0

'''
    Save temperature/rh figure/ pressure while time is betwen 23:45 - 0:00

'''
def save_weather_figure():
    url_lists = [
        'https://www.hko.gov.hk/wxinfo/ts/temp/ycttemp.png',
        'https://www.hko.gov.hk/wxinfo/ts/temp/twtemp.png',
        'https://www.hko.gov.hk/wxinfo/ts/temp/ktgtemp.png',
        'https://www.hko.gov.hk/wxinfo/ts/pre/hkopre.png'
    ]

    filenames = [
        'TaiPo',
        'ShingMunValley',
        'KwunTong',
        'HKO_Pressure'
    ]
    now = datetime.now()    
    if now.time().hour == 23 and now.time().minute > 55:            
    # if now.time().hour != 0:           
        for url_list, filename in zip(url_lists, filenames):
            format = '%Y%m%d'
            dt = now.strftime(format)             
            fname = filename + '_' + dt + '.jpg'
            if not os.path.exists(fname):       # if file not exist
                response = requests.get(url_list)
                with open(fname, "wb") as f:
                    print(f'save file: {fname}')
                    f.write(response.content)


''' 
Retriveve heat stress figure between 2:00 - 2:15
https://www.hko.gov.hk/wxinfo/ts/hkhi/kp_HKHI_comb_0711.png         King's Park
https://www.hko.gov.hk/wxinfo/ts/hkhi/br2_HKHI_comb_0718.png

'''
def save_heat_stress_figure():

    heat_urls = [
        'https://www.hko.gov.hk/wxinfo/ts/hkhi/kp_HKHI_comb_',
        'https://www.hko.gov.hk/wxinfo/ts/hkhi/br2_HKHI_comb_'
    ]

    heat_filenames = [
        'kp_HKHI_comb_',
        'br2_HKHI_comb_'
    ]

    now = datetime.now()    
    if now.time().hour == 2 and now.time().minute < 15:       
    # if now.time().hour != 0:
        for url, filename in zip(heat_urls, heat_filenames):
            d = now - timedelta(days=1)
            url = url + d.strftime('%m%d') + '.png'
            filename = filename + d.strftime('%m%d') + '.png'
            # print(url)
            if not os.path.exists(filename):       # if file not exist
                response = requests.get(url)
                with open(filename, "wb") as f:
                    print(f'save file: {filename}')
                    f.write(response.content)

def main():
    print('Read weather data Ver0-0')

    if len(sys.argv) == 2:
        period = int(sys.argv[1])
    else:
        period = 10
    print(f"Period: {period} seconds")

    temp_time, rh_time = init_last_time()
    while True:
        t, r = save_temperature_rh(temp_time, rh_time)
        if t != 0 or r != 0:
            temp_time, rh_time = t, r
        save_weather_figure()
        save_heat_stress_figure()
        now = datetime.now()
        print(now.strftime("%d/%m/%Y %H:%M:%S"))
        time.sleep(period)


if __name__ == "__main__":
    main()
