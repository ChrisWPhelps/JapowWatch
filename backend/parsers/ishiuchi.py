from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

# --- LIFT NAME MAPPING (Corrected for exact string matching) ---
LIFT_NAME_MAP = {
    'サンライズエクスプレス (チェア/ゴンドラ)': 'Sunrise Express (Chair/Gondola)',
    '中央ファミリーリフト': 'Central Family Lift',
    'チロルトリプルリフト': 'Tyrol Triple Lift',
    '中央高速トリプルリフト': 'Central Express Triple Lift',
    '山頂高速リフト': 'Summit Express Lift',
    '観光第1エクスプレス': 'Kanko No. 1 Express',
    '観光第2エクスプレス': 'Kanko No. 2 Express',
    '観光第3エクスプレス': 'Kanko No. 3 Express',
    '北丸山ファミリーペアリフト': 'Kita-Maruyama Family Pair Lift',
    'グリーンリフト': 'Green Lift',
    'ハツカ石第１トリプルリフト': 'Hatsukaishi No. 1 Triple Lift',
    'ハツカ石ファミリートリプルリフト/ペアリフト': 'Hatsukaishi Family Triple/Pair Lift',
    'ハツカ石スーパーリフト': 'Hatsukaishi Super Lift'
}


def get_data():
    home_url = 'https://ishiuchi.or.jp/winter/'
    lift_url = 'https://ishiuchi.or.jp/winter/ski/lift-course/#lift'

    driver = webdriver.Chrome()
    snow_depth = "0"
    lift_status_raw = {}

    try:
        # --- 1. SCRAPE SNOW FROM HOMEPAGE ---
        driver.get(home_url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "p-sales__txt")))
        time.sleep(2)
        home_soup = BeautifulSoup(driver.page_source, 'html.parser')

        sales_txt_div = home_soup.find('div', class_='p-sales__txt')
        if sales_txt_div:
            p_tags = sales_txt_div.find_all('p')
            for p in p_tags:
                text = p.get_text(strip=True)
                if '積雪' in text or 'Snow depth' in text:
                    match = re.search(r'(\d+)', text)
                    if match:
                        snow_depth = match.group(1)
                        break

        # --- 2. SCRAPE LIFTS FROM LIFT URL ---
        driver.get(lift_url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "table")))
        time.sleep(3)
        lift_soup = BeautifulSoup(driver.page_source, 'html.parser')

        lift_table = lift_soup.find('div', class_='table')
        if lift_table:
            rows = lift_table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    # Use separator to prevent text mashing
                    name_raw = cols[1].get_text(separator=" ", strip=True)
                    status_raw = cols[2].get_text(strip=True)

                    # Force clean whitespace: removes all tabs/newlines/extra spaces
                    name_clean = "".join(name_raw.split()) if "エクスプレス" in name_raw else " ".join(name_raw.split())
                    # Final fallback: just use the raw text if standard cleaning is too aggressive
                    name_final = name_raw.strip()

                    open_indicators = ['運行中', 'In operation', 'Operating', 'OPEN']
                    is_open = any(ind in status_raw for ind in open_indicators)

                    lift_status_raw[name_final] = 'Open' if is_open else 'Closed'

    except Exception as e:
        print(f"ISHIUCHI SCRAPE ERROR: {e}")
    finally:
        driver.quit()

    # --- 3. APPLY MAPPING ---
    lift_status_english = {}
    for jp_name, status in lift_status_raw.items():
        # Using a very loose match or direct key lookups
        en_name = LIFT_NAME_MAP.get(jp_name, jp_name)
        lift_status_english[en_name] = status

    return [
        {"resort_name": "Ishiuchi Maruyama"},
        {"Summit": snow_depth, "Base": snow_depth},
        {"Base": "0"},
        lift_status_english,
        {"last_updated": datetime.now().strftime('%Y-%m-%d %H:%M')}
    ]


if __name__ == "__main__":
    print(get_data())