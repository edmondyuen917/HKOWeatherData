import requests
import time
import os
import sys
# import datetime
from datetime import datetime, timezone, timedelta, date
from csv import reader
import pytz
import csv

url = 'https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en'
filename = 'latest_1min_pressure.csv'
temp_file_out = "temperature_log.csv"
rh_file_out = "rh_log.csv"


rh_site_list = [
    'Hong Kong Observatory'
]

site_list = [
    'King\'s Park',
    'Hong Kong Observatory',
    'Wong Chuk Hang',
    'Ta Kwu Ling',
    'Lau Fau Shan',
    'Tai Po',
    'Sha Tin',
    'Tuen Mun',
    'Tseung Kwan O',
    'Sai Kung',
    'Cheung Chau',
    'Chek Lap Kok',
    'Tsing Yi',
    'Tsuen Wan Ho Koon',
    'Tsuen Wan Shing Mun Valley',
    'Hong Kong Park',
    'Shau Kei Wan',
    'Kowloon City',
    'Happy Valley',
    'Wong Tai Sin',
    'Stanley',
    'Kwun Tong',
    'Sham Shui Po',
    'Kai Tak Runway Park',
    'Yuen Long Park',
    'Tai Mei Tuk',
    'Shek Kong'
]

def chk_output_file():
    if not os.path.exists(temp_file_out):
        s = 'Time,' 
        for site in site_list:
            s = s + site + ","
        with open(temp_file_out, "a") as f:
            print(s, file=f)

    if not os.path.exists(rh_file_out):
        s = 'Time,' 
        for site in rh_site_list:
            s = s + site + ","
        with open(rh_file_out, "a") as f:
            print(s, file=f)

def init_last_time():
    try:
        if not os.path.exists(temp_file_out):
            temp_last_update_time = datetime.fromisoformat("2022-12-31 00:00:00")
        else:
            with open(temp_file_out, "r") as tempfile:
                lines = tempfile.readlines()
                if len(lines) == 1:         # header only
                    temp_last_update_time = datetime.fromisoformat("2022-12-31 00:00:00")
                else:
                    line = lines [len(lines)-1].split(",")
                    format = '%m/%d/%Y %H:%M:%S'
                    temp_last_update_time = datetime.strptime(line[0], format) 
        tz = pytz.timezone('Asia/Hong_Kong')
        temp_last_update_time = tz.localize(temp_last_update_time, is_dst=None)

        if not os.path.exists(rh_file_out):
            rh_last_update_time = datetime.fromisoformat("2022-12-31 00:00:00")
        else:
            with open(rh_file_out, "r") as rhfile:
                lines = rhfile.readlines()
                if len(lines) == 1:         # header only
                    rh_last_update_time = datetime.fromisoformat("2022-12-31 00:00:00")
                else:
                    line = lines [len(lines)-1].split(",")
                    format = '%m/%d/%Y %H:%M:%S'
                    rh_last_update_time = datetime.strptime(line[0], format) 
        tz = pytz.timezone('Asia/Hong_Kong')
        rh_last_update_time = tz.localize(rh_last_update_time, is_dst=None)
        
        print(f'temperature last time: {temp_last_update_time}, RH last time: {rh_last_update_time}, ')
        return temp_last_update_time, rh_last_update_time
    
    except:
        print(Exception)
        print('initialize error!')
        return 0


def temperature_log(temp_last_update_time,rh_last_update_time):
    # print(f'temp_last_update_time: {temp_last_update_time},rh_last_update_time: {rh_last_update_time} ')
    try:
        response = requests.get(url)
        datas = response.json()
        updateTime = datas['updateTime']
        dt = datetime.fromisoformat(updateTime)
        if (dt > temp_last_update_time):
            print('record temperature')
            temp_last_update_time = dt
            s = dt.strftime("%m/%d/%Y %H:%M:%S") + ","
            temp_datas = datas['temperature']['data']
            temp_dict = {}
            for temp_data in temp_datas:
                temp_dict.update({temp_data['place']: int(temp_data['value'])})
            # print(temp_dict)
            # print(site_list)

            for site in site_list:
                if site in temp_dict:
                    value = str(temp_dict[site]) + ","
                else:
                    value = ','
                    print(f'{site} is not existed in download data')
                s = s + value 

            with open(temp_file_out, "a") as f:
                print(s)
                print(s, file=f)

        updateTime = datas['humidity']['recordTime']
        dt = datetime.fromisoformat(updateTime)
        if (dt > rh_last_update_time):
            print('record RH')
            rh_last_update_time = dt
            s = dt.strftime("%m/%d/%Y %H:%M:%S") + ","
            rh_datas = datas['humidity']['data']
            rh_dict ={}
            for rh_data in rh_datas:
                rh_dict.update({rh_data['place']: int(rh_data['value'])})

            for site in rh_site_list:
                if site in rh_dict:
                    value = str(rh_dict[site]) + ","
                else:
                    value = ','
                    print(f'{site} is not existed in download data')
                s = s + value 

            with open(rh_file_out, "a") as f:
                print(s)
                print(s, file=f)
        return temp_last_update_time, rh_last_update_time
    

    except:
        print('error!')
        return 0,0

     
def main():
    print('Temperature RH Loggging Ver0-0')

    for site in site_list:
        print(site)


    if len(sys.argv) == 2:
        period = int(sys.argv[1])
    else:
        period = 10
    print(f"Period: {period} seconds")

    chk_output_file()
    temp_time, rh_time = init_last_time()
    while True:
        t, r = temperature_log(temp_time, rh_time)
        if t != 0 or r != 0:
            temp_time, rh_time = t, r
        now = datetime.now()
        print(now.strftime("%d/%m/%Y %H:%M:%S"))
        time.sleep(period)

if __name__ == "__main__":
    main()
