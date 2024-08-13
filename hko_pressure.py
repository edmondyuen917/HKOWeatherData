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

'''

url = "https://data.weather.gov.hk/weatherAPI/hko_data/csdi/dataset/latest_1min_pressure_csdi_2.csv"
filename = 'pressure.csv'
output_file = "pressure_log.csv"


def init_last_time():
    try:
        if not os.path.exists(output_file):
            # p_last_update_time = datetime.fromisoformat('2024-01-01T10:11:00+08:00')
            p_last_update_time = datetime.fromisoformat("2022-12-31 00:00:00")
        else:
            with open(output_file, "r") as tempfile:
                lines = tempfile.readlines()
                line = lines [len(lines)-1].split(",")
                format = '%m/%d/%Y %H:%M:%S'
                p_last_update_time = datetime.strptime(line[0], format) 
                # dt = datetime.strptime(line[0], format) 
                # tz = pytz.timezone('Asia/Hong_Kong')
                # temp_last_update_time = tz.localize(dt, is_dst=None)
        print(f'init p_last_update_time: {p_last_update_time}')
        return p_last_update_time
    except:
        print(Exception)
        print('pressure error!')
        return 0


def pressure_log(p_time):
    try: 
        with open(filename, "wb") as f:
            response = requests.get(url)
            f.write(response.content)        

        with open(filename,"r",encoding="utf-8") as csvfile:
            csv_reader = reader((csvfile), delimiter=",")
            list_of_rows = list(csv_reader)
            del list_of_rows[0]             # remove the first row
            # print("Raw row = ", len(list_of_rows))            
                
        for line in list_of_rows:
            year = line[0]
            month = line[1]
            day = line[2]
            hour = line[3]
            minute = line[4]
            station = line[7]
            pressure  = line[8]
            d = datetime(int(year), int(month), int(day), int(hour), int(minute), 0)

            if (d > p_time):
                p_time = d
                with open(output_file, "a") as f:
                    s = d.strftime("%m/%d/%Y %H:%M:%S") + "," + station + ',' + pressure
                    print(s)
                    print(s, file=f)
        return p_time
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

    p_time = init_last_time()
    while True:
        p_temp = pressure_log(p_time)
        if p_temp != 0:  p_time = p_temp
        now = datetime.now()
        print(now.strftime("%d/%m/%Y %H:%M:%S"))
        time.sleep(period)

if __name__ == "__main__":
    main()
