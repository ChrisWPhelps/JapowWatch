import sys
sys.stdout.reconfigure(encoding='utf-8')

import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup


# Map SVG <g> id values to human-readable lift names
LIFT_NAMES = [
    "PANORAMA No.1",
    "PANORAMA No.2",
    "Summit Express",
    "PARADISE",
    "EIGHT gondola",
    "SHIRAKABA No.1",
    "SHIRAKABA No.2",
    "SHIRAKABA No.3",
    "SEIKADAI No.1",
    "Snow Escalater",
]

# Map SVG class to readable status
STATUS_MAP = {
    "is-open":        "Open",
    "is-stop":        "Closed",
    "is-preparation": "Preparation",
}


def get_soup():
    url = 'https://sapporo-teine.com/snow/lang/en/trailstatus/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.text, 'html.parser')


def get_teine_snow_data(soup):
    # div.gnav2023__child__data__item > div.gnav2023__child__data__count
    #   <p class="num">285cm</p>
    #   <p class="en">Peak-depth</p>
    data_items = soup.find_all("div", class_="gnav2023__child__data__item")

    snow_data = {}
    for item in data_items:
        count_div = item.find("div", class_="gnav2023__child__data__count")
        if not count_div:
            continue
        num_p   = count_div.find("p", class_="num")
        label_p = count_div.find("p", class_="en")
        if num_p and label_p:
            snow_data[label_p.get_text(strip=True)] = num_p.get_text(strip=True)

    def parse_cm(val):
        if val is None:
            return None
        m = re.search(r'(\d+)', val)
        return int(m.group(1)) if m else None

    return [{"Niseko":   parse_cm(snow_data.get("Peak-depth"))}, 
            {"Niseko": parse_cm(snow_data.get("24 hour snowfall amount"))}]


def get_teine_lift_status(soup):
    # Lift status is in an SVG map inside div.greport-map__map
    # Each lift is a <g id="liftname" class="is-open|is-stop|is-preparation">
    svg = soup.select_one("div.greport-map__map svg")
    if not svg:
        return {}

    lift_dic = {}
    i = 0
    for g in svg.find_all("g", id=True):
        if i > 9:
            break
        lift_id = g.get("id")
        classes = g.get("class", [])

        # Find which status class is present
        status = None
        for cls in classes:
            if cls in STATUS_MAP:
                status = STATUS_MAP[cls]
                break

        if status != "Open":
            status = "Closed"

        if status:
            name = LIFT_NAMES[i]
            lift_dic[name] = status
        
        i = i+1

    return lift_dic


def get_data():
    soup = get_soup()

    resort_name  = {"resort_name": "Sapporo Teine"}
    snow         = get_teine_snow_data(soup)
    last_updated = {"last_updated": datetime.now().strftime('%Y-%m-%d %H:%M')}
    lifts        = get_teine_lift_status(soup)

    return [resort_name, snow[0], snow[1], lifts, last_updated]


if __name__ == "__main__":
    print(get_data())