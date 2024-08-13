import requests
import time
import os
import sys
# import datetime
from datetime import datetime, timezone, timedelta
from csv import reader
import pytz
import temp_rh_log, latest_1min_pressure
# print('Number of arguments:', len(sys.argv), 'arguments.')
# print('Argument List:', str(sys.argv))



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

    temp_rh_log.chk_output_file()
    temp_time, rh_time = temp_rh_log.init_last_time()

    latest_1min_pressure.chk_output_file()
    p_time = latest_1min_pressure.init_last_time()

    while True:
        t, r = temp_rh_log.temperature_log(temp_time, rh_time)
        if t != 0 or r != 0:
            temp_time, rh_time = t, r

        p = latest_1min_pressure.pressure_log(p_time)
        if p != 0:  p_time  = p

        save_weather_figure()
        save_heat_stress_figure()

        now = datetime.now()
        print(now.strftime("%d/%m/%Y %H:%M:%S"))
        time.sleep(period)

if __name__ == "__main__":
    main()
