import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_snow_data():
    url = 'https://www.sapporo-kokusai.jp/'
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    cent = soup.find_all(string = 'cm')

    snow_data = []


    for cm_span in cent:
        parent = cm_span.find_parent("div", class_="realtime__text_large")
        count = parent.find("p", class_="realtime__text_count")
        number = count.get_text(strip=True).replace("cm", "").strip()
        snow_data.append(number)

    return [{"Sapporo Kokusai": snow_data[1]}, {"Sapporo Kokusai": snow_data[0]}]

def get_lift_status():
    url = 'https://www.sapporo-kokusai.jp/slopes/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    STATUS_MAP = {
        'service':   'Open',
        'scheduled': 'Closed',
        'suspend':   'Closed',
        'stop':      'Closed',
    }

    lifts = ['SkyCabin8', 'Marchen Quad Lift', 'Echo Quad Lift', 'Woody Pair Lift', 'Snow Escalator']

    status_list = []

    for g in soup.find_all('g', id=lambda x: x and ('リフト' in x or 'キャビン' in x or 'ゴンドラ' in x)):
        classes = g.get('class', [])
        status = next((STATUS_MAP[c] for c in classes if c in STATUS_MAP), 'Closed')
        status_list.append(status)

    result = dict(zip(lifts, status_list))

    return result



def get_data():
    last_updated = {"last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")}

    return [
        {"resort_name": "Sapporo Kokusai"},
        get_snow_data()[0],
        get_snow_data()[1],
        get_lift_status(),
        last_updated,
    ]