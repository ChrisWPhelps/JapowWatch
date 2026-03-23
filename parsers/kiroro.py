import sys
import io
import requests
from bs4 import BeautifulSoup

from datetime import datetime

import re


def get_snow():

    url = 'https://www.kiroro.co.jp/dashboard/'
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    matches = re.findall(r'(\d+)cm', response.text)

    snowdepth_dic = {"Kiroro" : matches[0]}

    snowfall_dic = {"Kiroro" : matches[2]}

    return [snowdepth_dic, snowfall_dic]



def get_lift_status():
    url = 'https://www.kiroro.co.jp/dashboard/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    status_table = soup.find("div", class_ = 'operation-status operation-status--lift')
    status_inner = status_table.find("div", class_ = 'operation-status__inner')

    boxes = status_inner.find_all("div")

    liftstatus_dic = {}

    for box in boxes:
        lift_name = box.find(string=True, recursive=False).strip().strip('"')

        lift_span = box.find("span")

        status = "Closed"

        if "Operating" in lift_span.get_text():
            status = "Operating"
        
        liftstatus_dic.update({lift_name : status})


    return liftstatus_dic

def get_data():
    resort_name = {"resort_name" : "Kiroroo Snow World"}
    last_updated = {"last_updated" : datetime.now().strftime('%Y-%m-%d %H:%M')}

    final_return = [resort_name, 
                    get_snow()[0], 
                    get_snow()[1],
                    get_lift_status(),
                    last_updated]
    
    return final_return

print (get_data())
