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

site_list = []
rh_site_list = []

'''
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
'''

def temperature_log():
    try:
        # initialize temperature site_list & last_time from output file        
        if not os.path.exists(temp_file_out):
            s = 'Time' 
            with open(temp_file_out, "a") as f:
                print(s, file=f)
            site_list = []
            temp_last_update_time = datetime.fromisoformat("2022-12-31 00:00:00")            
        else:
            with open(temp_file_out,"r",encoding="utf-8") as csvfile:
                csv_reader = reader((csvfile), delimiter=",")
                list_of_rows = list(csv_reader)
                site_list = list_of_rows[0]
                del site_list[0]        # delete "TIME" item

                if len(list_of_rows) == 1:         # header only
                    temp_last_update_time = datetime.fromisoformat("2022-12-31 00:00:00")
                else:
                    line = list_of_rows [len(list_of_rows)-1]
                    format = '%m/%d/%Y %H:%M:%S'
                    temp_last_update_time = datetime.strptime(line[0], format) 
        tz = pytz.timezone('Asia/Hong_Kong')
        temp_last_update_time = tz.localize(temp_last_update_time, is_dst=None)
                
        # initialize RH site_list & last_time from output file                                
        if not os.path.exists(rh_file_out):
            s = 'Time' 
            with open(rh_file_out, "a") as f:
                print(s, file=f)
            rh_site_list =[]
            rh_last_update_time = datetime.fromisoformat("2022-12-31 00:00:00")            
        else:
            with open(rh_file_out,"r",encoding="utf-8") as csvfile:
                csv_reader = reader((csvfile), delimiter=",")
                list_of_rows = list(csv_reader)
                rh_site_list = list_of_rows[0]
                del rh_site_list[0]        # delete "TIME" item

                if len(list_of_rows) == 1:         # header only
                    rh_last_update_time = datetime.fromisoformat("2022-12-31 00:00:00")
                else:
                    line = list_of_rows [len(list_of_rows)-1]
                    format = '%m/%d/%Y %H:%M:%S'
                    rh_last_update_time = datetime.strptime(line[0], format) 
        tz = pytz.timezone('Asia/Hong_Kong')
        rh_last_update_time = tz.localize(rh_last_update_time, is_dst=None)
        # print(f'temperature last time: {temp_last_update_time}, RH last time: {rh_last_update_time}, ')

        # download data from API
        response = requests.get(url)
        datas = response.json()
        updateTime = datas['temperature']['recordTime']
        dt = datetime.fromisoformat(updateTime)
        if (dt > temp_last_update_time):
            print('record temperature')
            temp_last_update_time = dt

            temp_datas = datas['temperature']['data']
            temp_dict = {}
            for temp_data in temp_datas:
                temp_dict.update({temp_data['place']: int(temp_data['value'])})
                    
            # check if any new site in download data
            new_sites = []
            dict_keys = temp_dict.keys()
            for dict_key in dict_keys:
                if dict_key not in site_list:
                    new_sites.append(dict_key)

            if (new_sites):
                with open('temp.csv','w') as fw, open(temp_file_out,'r') as fr:
                    lines = fr.readlines()
                    for new_site in new_sites:
                        lines[0] = lines[0].strip('\n') + ',' +  new_site 
                        site_list.append(new_site)
                    for line in lines:
                        print(line, file = fw)

                os.remove(temp_file_out)                        
                os.rename('temp.csv', temp_file_out)

            # update data   
            s = dt.strftime("%m/%d/%Y %H:%M:%S")
            for site in site_list:
                if site in temp_dict:
                    value = ',' + str(temp_dict[site]) 
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
            rh_datas = datas['humidity']['data']
            rh_dict ={}
            for rh_data in rh_datas:
                rh_dict.update({rh_data['place']: int(rh_data['value'])})

            # check if any new site in download data
            new_sites = []
            dict_keys = rh_dict.keys()
            for dict_key in dict_keys:
                if dict_key not in rh_site_list:
                    new_sites.append(dict_key)

            if (new_sites):
                with open('temp.csv','w') as fw, open(rh_file_out,'r') as fr:
                    lines = fr.readlines()
                    for new_site in new_sites:
                        lines[0] = lines[0].strip('\n') + ',' + new_site 
                        rh_site_list.append(new_site)
                    for line in lines:
                        print(line.strip('\n'), file = fw)

                os.remove(rh_file_out)                        
                os.rename('temp.csv', rh_file_out)

            # update data   
            s = dt.strftime("%m/%d/%Y %H:%M:%S")
            for site in rh_site_list:
                if site in rh_dict:
                    value =',' + str(rh_dict[site]) 
                else:
                    value = ','
                    print(f'{site} is not existed in download data')
                s = s + value 

            with open(rh_file_out, "a") as f:
                print(s)
                print(s, file=f)

    except:
        print('temp/rh log error!')
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


    # temp_time, rh_time = init()
    while True:
        # t, r = temperature_log(temp_time, rh_time)
        # if t != 0 or r != 0:
        #     temp_time, rh_time = t, r
        temperature_log()
        now = datetime.now()
        print(now.strftime("%d/%m/%Y %H:%M:%S"))
        time.sleep(period)

if __name__ == "__main__":
    main()
