import requests
import time
import os
import sys
# import datetime
from datetime import datetime, timezone, timedelta, date
from csv import reader
import pytz

'''
Retriveve heat stress figure
https://www.hko.gov.hk/wxinfo/ts/hkhi/kp_HKHI_comb_0711.png         King's Park
https://www.hko.gov.hk/wxinfo/ts/hkhi/br2_HKHI_comb_0718.png

'''

urls = [
    'https://www.hko.gov.hk/wxinfo/ts/hkhi/kp_HKHI_comb_',
    'https://www.hko.gov.hk/wxinfo/ts/hkhi/br2_HKHI_comb_'
]

filenames = [
    'kp_HKHI_comb_',
    'br2_HKHI_comb_'
]


def main():
    start_date = date(2024,7,22)
    now = datetime.now()    
    end_date = now.date()
    delta = timedelta(days=1)

    while (start_date < end_date):
        for url, filename in zip(urls, filenames):
            url = url + start_date.strftime('%m%d') + '.png'
            filename = filename + start_date.strftime('%m%d') + '.png'
            print(url)
            response = requests.get(url)
            with open(filename, "wb") as f:
                print(f'save file: {filename}')
                f.write(response.content)

        print(start_date, end="\n")
        start_date += delta


if __name__ == "__main__":
    main()
