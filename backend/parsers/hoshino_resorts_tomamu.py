import requests
from bs4 import BeautifulSoup

from datetime import datetime

def get_all():
    url = "https://www.snowtomamu.jp/winter/en/ski/ski-slope/condition/"
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, headers=headers)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    snowfall_div = soup.select(".condition-snowfall")
    details = snowfall_div[0].select(".condition-item-detail")

    snow_depth = details[0].get_text(strip=True).strip()

    snowdepth_dic = {'Tomamu' : snow_depth}

    snowfall = snowfall_div[1].select_one(".condition-item-detail").get_text(strip=True).strip()

    snowfall_dic = {'Tomamu' : snowfall}


    lifts = {}
    for div in soup.select(".lift-map .lift-name"):
        name = div.get_text(strip=True)
        classes = div.get("class", [])
        if "is-running" in classes:
            status = "Open"
        else:
            status = "Closed"
        lifts[name] = status

    return [snowdepth_dic, snowfall_dic, lifts]

def get_data():
    resort_name = {"resort_name" : "Hoshino Resorts TOMAMU"}
    last_updated = {"last_updated" : datetime.now().strftime('%Y-%m-%d %H:%M')}

    final_return = [resort_name, 
                    get_all()[0], 
                    get_all()[1],
                    get_all()[2],
                    last_updated]
    
    return final_return


if __name__ == "__main__":
    print(get_data())