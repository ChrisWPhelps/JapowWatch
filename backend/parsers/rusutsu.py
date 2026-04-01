import requests
from bs4 import BeautifulSoup

from datetime import datetime

import sys
sys.stdout.reconfigure(encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import re

# Site uses "--cm" when closed or a metric is not published; treat as 0 for the contract.
_CM_TOKEN = re.compile(r"(\d+|--)cm")


def _rusutsu_cm_to_str(token: str) -> str:
    return "0" if token == "--" else token


def get_snow_data():
    url = 'https://rusutsu.com/en/snow-and-weather-report/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    matches = _CM_TOKEN.findall(response.text)
    if len(matches) < 8:
        raise ValueError(
            f"Rusutsu snow page: expected at least 8 '(digits|-- )cm' tokens, got {len(matches)}"
        )

    snowdepth = [
        _rusutsu_cm_to_str(matches[0]),
        _rusutsu_cm_to_str(matches[3]),
        _rusutsu_cm_to_str(matches[6]),
    ]
    snowfall = [
        _rusutsu_cm_to_str(matches[1]),
        _rusutsu_cm_to_str(matches[4]),
        _rusutsu_cm_to_str(matches[7]),
    ]

    mountains = ['West Mt.', 'East Mt.', 'Mt. Isola']

    snowdepth_dic = dict(zip(mountains, snowdepth))
    snowfall_dic = dict(zip(mountains, snowfall))

    return [snowdepth_dic, snowfall_dic]

def get_lift_status():
    driver = webdriver.Chrome()  # or Firefox
    driver.get('https://rusutsu.com/en/lift-and-trail-status/')

    # Wait until the ul is populated
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.status-list li"))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    table = soup.find("ul", class_='status-list encode_on')
    
    status_list = table.find_all("b", class_='notranslate')

    lift_names = ['Yotei gondola', 'West No.1 Quad Lift', 'West No.2 Quad Lift', 'West Tiger Pair Lift', 'East No.1 Gondola', 'East No.2 Gondola', 'East Quad Lift', 'East No.1 Pair Lift', 'East No.2 Pair Lift', 'Tower Pair Lift', 'Isola Gondola', 'Across No.1 Pair Lift', 'Across No.2 Pair Lift', 'Isola No.1 Quad Lift', 'Isola No.2 Quad Lift', 'Isola No.3 Quad Lift', 'Isola No.4 Quad Lift', 'Isola No.5 Pair Lift']
    lift_status = []

    for status in status_list:
        lift_status.append(status.text)

    
    lift_dic = dict(zip(lift_names, lift_status))

    return lift_dic

def get_data():
    resort_name = {"resort_name" : "Rusutsu Resort"}
    last_updated = {"last_updated" : datetime.now().strftime('%Y-%m-%d %H:%M')}

    snow_depth_dic, snowfall_dic = get_snow_data()
    final_return = [
        resort_name,
        snow_depth_dic,
        snowfall_dic,
        get_lift_status(),
        last_updated,
    ]

    return final_return


if __name__ == "__main__":
    print(get_data())
