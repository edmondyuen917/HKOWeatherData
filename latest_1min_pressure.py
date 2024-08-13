import requests
import time
import os
import sys
# import datetime
from datetime import datetime, timezone, timedelta, date
from csv import reader
import pytz
import csv


'''
https://data.weather.gov.hk/weatherAPI/hko_data/csdi/dataset/latest_1min_pressure_csdi_2.csv

https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_1min_pressure.csv

'''

url = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_1min_pressure.csv"
filename = 'latest_1min_pressure.csv'
output_file = "latest_1min_pressure_log.csv"


site_list = [
    'Chek Lap Kok',
    'Cheung Chau',
    'HK Observatory',
    'Lau Fau Shan',
    'Peng Chau',
    'Sha Tin',
    'Shek Kong',
    'Sheung Shui',
    'Ta Kwu Ling',
    'Tai Po',
    'Waglan Island',
    'Wetland Park'
]

def chk_output_file():
    if not os.path.exists(output_file):
        s = 'Time,' 
        for site in site_list:
            s = s + site + ","
        with open(output_file, "a") as f:
            print(s, file=f)

def init_last_time():
    try:
        if not os.path.exists(output_file):
            last_update_time = datetime.fromisoformat("2022-12-31 00:00:00")
        else:
            with open(output_file, "r") as tempfile:
                lines = tempfile.readlines()
                if len(lines) == 1:         # header only
                    last_update_time = datetime.fromisoformat("2022-12-31 00:00:00")
                else:
                    line = lines [len(lines)-1].split(",")
                    format = '%m/%d/%Y %H:%M:%S'
                    last_update_time = datetime.strptime(line[0], format) 
        print(f'init p_last_update_time: {last_update_time}')
        return last_update_time
    
    except:
        print(Exception)
        print('pressure error!')
        return 0

# def pressure_log(p_time):
def pressure_log(last_time):
    try: 
        with open(filename, "wb") as f:
            response = requests.get(url)
            f.write(response.content)        

        pressure_dict = {}
        with open(filename,"r",encoding="utf-8") as csvfile:
            csv_reader = reader((csvfile), delimiter=",")
            list_of_rows = list(csv_reader)
            del list_of_rows[0]             # remove the first row
            for line in list_of_rows:
                timestamp = line[0]
                pressure_dict.update({line[1]: line[2]})


        year = int(timestamp[0:4])
        month = int(timestamp[4:6])
        day = int(timestamp[6:8])
        hour = int(timestamp[8:10])
        minute = int(timestamp[10:12])
        t = datetime(year, month, day, hour, minute, 0)

        if (t > last_time):
            s = (t.strftime("%m/%d/%Y %H:%M:%S")) + ','
            for site in site_list:
                if site in pressure_dict:
                    value = str(pressure_dict[site] + ",")
                else:
                    value = ','
                    print(f'{site} is not existed in pressure download data')
                s = s + value

            with open(output_file, "a") as f:
                print(s)
                print(s, file=f)
        return t

    except:
        print(Exception)
        print('pressure error!')
        return 0    


     
def main():
    print('Pressure Loggging Ver0-0')

    if len(sys.argv) == 2:
        period = int(sys.argv[1])
    else:
        period = 10
    print(f"Period: {period} seconds")

    chk_output_file()


    last_time = init_last_time()
    while True:
        last_time_temp = pressure_log(last_time)
        if last_time_temp != 0:  last_time  = last_time_temp
        now = datetime.now()
        print(now.strftime("%d/%m/%Y %H:%M:%S"))
        time.sleep(period)

if __name__ == "__main__":
    main()
