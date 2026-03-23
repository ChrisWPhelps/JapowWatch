import sys
import io
import requests
from bs4 import BeautifulSoup

from datetime import datetime


def get_snow():
    # url that contains snow depth + snowfall data
    url = 'https://www.happo-one.jp/en/'
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    

    # Finds all elements that contain the text 'SnowDepth'
    snow_depth = soup.find_all(string = 'SnowDepth')

    # Finds the numerical value in the parent of each 'SnowDepth' element and stores in an array as a string value. html structure is as follows.
    #    <li class="en">
    #        <span class="label">SnowDepth</span>
    #        <strong>245</strong>cm
    #    </li>
    for i in range(3):
        snow_depth[i] = snow_depth[i].parent.parent.find('strong').string

    mountains = ['Kurobishi', 'Usagidaira', 'Nakiyama']

    snowdepth_dic = dict(zip(mountains, snow_depth))

    snowfall = soup.find_all(string = 'SnowFall')

    for i in range(3):
        snowfall[i] = snowfall[i].parent.parent.find('strong').string

    snowfall_dic = dict(zip(mountains, snowfall))

    return [snowdepth_dic, snowfall_dic]



def get_lift_status():
    url = 'https://www.happo-one.jp/en/gelande/lift-report/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table')
    rows = table.find_all('tr')

    liftstatus_dic = {}

    for row in rows[1:]: 
        cols = row.find_all('td')
        if len(cols) < 2:
            continue

        name = cols[0].get_text(strip=True)
        img = cols[1].find('img')

        src = img.get('src', '')
        if 'circle' in src:
            status = 'Open'
        else:
            status = 'Closed'

        liftstatus_dic.update({name : status})

    return liftstatus_dic

def get_data():
    resort_name = {"resort_name" : "Hakuba Happo-One"}
    last_updated = {"last_updated" : datetime.now().strftime('%Y-%m-%d %H:%M')}

    final_return = [resort_name, 
                    get_snow()[0], 
                    get_snow()[1],
                    get_lift_status(),
                    last_updated]
    
    return final_return

print (get_data())
