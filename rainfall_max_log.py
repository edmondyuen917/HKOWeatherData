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
rainfall_max_file_out = "rainfall_max_log.csv"

site_list = []

def log():
    try:
        # initialize temperature site_list & last_time from output file        
        if not os.path.exists(rainfall_max_file_out):
            s = 'StartTime,EndTime' 
            with open(rainfall_max_file_out, "a") as f:
                print(s, file=f)
            site_list = []
            last_update_time = datetime.fromisoformat("2022-12-31 00:00:00")            
        else:
            with open(rainfall_max_file_out,"r",encoding="utf-8") as csvfile:
                csv_reader = reader((csvfile), delimiter=",")
                list_of_rows = list(csv_reader)
                site_list = list_of_rows[0]
                del site_list[0:2]        # delete "StartTime" and "EndTime"

                if len(list_of_rows) == 1:         # header only
                    last_update_time = datetime.fromisoformat("2022-12-31 00:00:00")
                else:
                    line = list_of_rows [len(list_of_rows)-1]
                    format = '%m/%d/%Y %H:%M:%S'
                    last_update_time = datetime.strptime(line[0], format) 
        tz = pytz.timezone('Asia/Hong_Kong')
        last_update_time = tz.localize(last_update_time, is_dst=None)
                
        # download data from API
        response = requests.get(url)
        datas = response.json()
        StartTime = datas['rainfall']['startTime']
        EndTime = datas['rainfall']['endTime']
        StartTime = datetime.fromisoformat(StartTime)
        EndTime = datetime.fromisoformat(EndTime)
        if (StartTime > last_update_time):
            print('record rain fall')
            last_update_time = StartTime

            temp_datas = datas['rainfall']['data']
            dict_data = {}
            for temp_data in temp_datas:
                if 'max' in temp_data:
                    max = temp_data['max']
                else:
                    max = 'NA'
                dict_data.update({temp_data['place']: max})
                    
            # check if any new site in download data
            new_sites = []
            dict_keys = dict_data.keys()
            for dict_key in dict_keys:
                if dict_key not in site_list:
                    new_sites.append(dict_key)

            if (new_sites):
                with open('temp.csv','w') as fw, open(rainfall_max_file_out,'r') as fr:
                    lines = fr.readlines()
                    for new_site in new_sites:
                        lines[0] = lines[0].strip('\n') + ',' +  new_site 
                        site_list.append(new_site)
                    for line in lines:
                        print(line.strip('\n'), file = fw)                        

                os.remove(rainfall_max_file_out)                        
                os.rename('temp.csv', rainfall_max_file_out)

            # update data   
            s = StartTime.strftime("%m/%d/%Y %H:%M:%S") + ',' + EndTime.strftime("%m/%d/%Y %H:%M:%S")
            for site in site_list:
                if site in dict_data:
                    value = ',' + str(dict_data[site]) 
                else:
                    value = ','
                    print(f'{site} is not existed in download data')
                s = s + value 

            with open(rainfall_max_file_out, "a") as f:
                print(s)
                print(s, file=f)

    except:
        print('rainfall log error!')
        return 0,0

     
def main():
    print('Rain fall Loggging Ver0-0')

    for site in site_list:
        print(site)


    if len(sys.argv) == 2:
        period = int(sys.argv[1])
    else:
        period = 10
    print(f"Period: {period} seconds")

    while True:
        log()
        now = datetime.now()
        print(now.strftime("%d/%m/%Y %H:%M:%S"))
        time.sleep(period)

if __name__ == "__main__":
    main()
