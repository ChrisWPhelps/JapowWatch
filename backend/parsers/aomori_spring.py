import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

try:
    from parsers.snow_contract import normalize_depth_value
except ModuleNotFoundError:
    # Running as `python parsers/aomori_spring.py` (cwd backend): package root not on path
    from snow_contract import normalize_depth_value


def get_snow():
    url = 'https://aomorispring.com/ski/lift-course-status'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    depth = "0"
    fall = "0"

    # We find the label 'Snowfall' or 'Snow Depth' from your image
    # and then grab the 'font-bold' span inside the very next container
    depth_label = soup.find('span', string=re.compile(r'Snow Depth', re.I))
    fall_label = soup.find('span', string=re.compile(r'Snowfall', re.I))

    if depth_label:
        val = depth_label.find_next('span', class_='font-bold')
        if val:
            depth = normalize_depth_value(val.get_text(strip=True))

    if fall_label:
        val = fall_label.find_next('span', class_='font-bold')
        if val:
            fall = normalize_depth_value(val.get_text(strip=True))

    # THE SWAP: If the 'fall' we found is huge (the 420) and depth is 0,
    # we know the labels on the site are effectively swapped for our DB
    if int(fall) > 100 and depth == "0":
        depth, fall = fall, "0"

    mountains = ['Resort Base']
    return [{mountains[0]: depth}, {mountains[0]: fall}]


def get_lift_status():
    url = 'https://aomorispring.com/ski/lift-course-status'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    liftstatus_dic = {}

    tables = soup.find_all('table')
    for table in tables:
        headers = [h.get_text().lower() for h in table.find_all('th')]
        if 'lift' in headers or 'status' in headers:
            rows = table.find_all('tr')
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    name = cols[0].get_text(strip=True)
                    status_text = cols[1].get_text(strip=True).lower()
                    status = 'Open' if 'open' in status_text or '運行' in status_text else 'Closed'
                    liftstatus_dic[name] = status
            break
    return liftstatus_dic


def get_data():
    resort_name = {"resort_name": "Aomori Spring"}
    last_updated = {"last_updated": datetime.now().strftime('%Y-%m-%d %H:%M')}
    snow_data = get_snow()
    return [resort_name, snow_data[0], snow_data[1], get_lift_status(), last_updated]


if __name__ == "__main__":
    print(get_data())