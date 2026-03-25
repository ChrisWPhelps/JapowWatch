import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_snow():
    url = 'https://www.hakubavalley.com/en/weather_en/detail_cortina_en/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Default values in case the site structure shifts
    depth = "0"
    fall = "0"

    # The weather info is in the first table on the page
    weather_table = soup.find('table')
    if weather_table:
        # We look for the row containing the resort name (sometimes in Japanese)
        rows = weather_table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            # The row with 'Hakuba Cortina' (or its Japanese name) contains the data
            if len(cells) >= 5:
                depth = cells[2].get_text(strip=True)  # Snow Depth column
                fall = cells[3].get_text(strip=True)  # Today's Snowfall column
                break

    mountains = ['Cortina Area']
    return [{mountains[0]: depth}, {mountains[0]: fall}]


def get_lift_status():
    url = 'https://www.hakubavalley.com/en/weather_en/detail_cortina_en/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    liftstatus_dic = {}

    # Lift status is in the second table on these detail pages
    tables = soup.find_all('table')
    if len(tables) > 1:
        lift_table = tables[1]
        rows = lift_table.find_all('tr')

        for row in rows[1:]:  # Skip the header row
            cols = row.find_all('td')
            if len(cols) >= 2:
                name = cols[0].get_text(strip=True)
                status_text = cols[1].get_text(strip=True)

                # Standardize status to 'Open' or 'Closed'
                status = 'Open' if 'OPEN' in status_text.upper() else 'Closed'
                liftstatus_dic[name] = status

    return liftstatus_dic


def get_data():
    resort_name = {"resort_name": "Hakuba Cortina"}
    last_updated = {"last_updated": datetime.now().strftime('%Y-%m-%d %H:%M')}

    snow_data = get_snow()

    return [
        resort_name,
        snow_data[0],
        snow_data[1],
        get_lift_status(),
        last_updated
    ]


if __name__ == "__main__":
    print(get_data())