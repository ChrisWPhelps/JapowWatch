import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- LIFT NAME MAPPING ---
# Translating Japanese lift and course names to English for the frontend
LIFT_NAME_MAP = {
    '第1リフト': 'No.1 Lift',
    '第2クワッドリフト': 'No.2 Quad Lift',
    '第3リフト': 'No.3 Lift',
    '第5リフト': 'No.5 Lift',
    'スーパークワッドリフト': 'Super Quad Lift',
    '第11リフト': 'No.11 Lift',
    '第12リフト': 'No.12 Lift',
    '第13リフト': 'No.13 Lift',
    '第15リフト': 'No.15 Lift',
    'スノーパーク': 'Snow Park',
    'キッズパーク': 'Kids Park',
    'パウダーシアター': 'Powder Theater',
    'パウダーウェーブ2': 'Powder Wave 2',
    'リバーライン': 'River Line',
    'クリスタルボウル': 'Crystal Bowl',
    'カモシカコース': 'Kamoshika Course',
    'ベアーコース': 'Bear Course',
    'ラビットコース': 'Rabbit Course'
}

def get_data():
    snow_url = "https://www.madarao.jp/ski"
    lift_url = "https://www.madarao.jp/ski/conditions"
    resort_name = "Madarao Mountain Resort"

    snow_depth = "0"
    lift_status_dic = {}
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")

    try:
        # 1. SCRAPE SNOW DEPTH
        s_res = requests.get(snow_url, timeout=10)
        s_soup = BeautifulSoup(s_res.text, 'html.parser')

        condition_inner = s_soup.find('div', class_='bar-condition-inner')
        if condition_inner:
            dls = condition_inner.find_all('dl')
            for dl in dls:
                dt = dl.find('dt')
                if dt and "積雪" in dt.text:
                    snow_depth = dl.find('strong').text.strip().replace('cm', '')

        # 2. SCRAPE LIFT STATUS
        l_res = requests.get(lift_url, timeout=10)
        l_soup = BeautifulSoup(l_res.text, 'html.parser')

        lift_table = l_soup.find('table', class_='is-full is-max-full')
        if lift_table:
            rows = lift_table.find_all('tr')
            for row in rows:
                th = row.find('th')
                td = row.find('td', class_='is-center')

                if th and td:
                    name_raw = th.get_text(strip=True)
                    raw_status = td.get_text(strip=True)

                    # Standardization Mapping
                    status_map = {
                        "運休": "Closed",
                        "営業終了": "Closed",
                        "準備中": "Closed",
                        "終了": "Closed",
                        "": "Closed"
                    }

                    if raw_status in status_map:
                        status = "Closed"
                    elif any(char.isdigit() for char in raw_status) or "中" in raw_status:
                        status = "Open"
                    else:
                        status = "Closed"

                    # Apply English Mapping
                    name_en = LIFT_NAME_MAP.get(name_raw, name_raw)
                    lift_status_dic[name_en] = status

    except Exception as e:
        print(f"MADARAO SCRAPE ERROR: {e}")
        return None

    # --- 3. DATA CONTRACT COMPLIANCE ---
    return [
        {"resort_name": resort_name},
        {"Base": snow_depth},
        {"New Snow": "0"},
        lift_status_dic,
        {"last_updated": last_updated}
    ]


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_data())