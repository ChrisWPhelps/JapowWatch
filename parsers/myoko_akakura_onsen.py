from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

# --- LIFT NAME MAPPING (Matched to image_7a6fc4.jpg) ---
LIFT_NAME_MAP = {
    'ヨーデル第1トリプル': 'Yodel No. 1 Triple',
    'ヨーデル第2クワッド': 'Yodel No. 2 Quad',
    'ヨーデル第3トリプル': 'Yodel No. 3 Triple',
    'ヨーデル第4ペア': 'Yodel No. 4 Pair',
    'ヨーデル第5トリプル': 'Yodel No. 5 Triple',
    'くまどー第1クワッド': 'Kumado No. 1 Quad',
    'くまどー第2ペア': 'Kumado No. 2 Pair',
    'くまどー第3ペア': 'Kumado No. 3 Pair',
    'くまどー第4トリプル': 'Kumado No. 4 Triple',
    'くまどー第5ペア': 'Kumado No. 5 Pair',
    '銀嶺第1ペア': 'Ginrei No. 1 Pair',
    '銀嶺第2ペア': 'Ginrei No. 2 Pair',
    '銀嶺第3ペア': 'Ginrei No. 3 Pair',
    '銀嶺第5ペア': 'Ginrei No. 5 Pair'
}


def get_data():
    url = 'https://akakura-ski.com/gelande/'
    driver = webdriver.Chrome()

    snow_depth = "0"
    lift_status_dic = {}

    try:
        driver.get(url)

        # 1. WAIT FOR TABLE
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "normal"))
        )
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # --- 2. TARGET SNOW DATA ---
        base_factors = soup.find_all('li', class_='sub')
        for item in base_factors:
            if item.find('i', class_=re.compile(r'fa-snowflake')):
                text = item.get_text(strip=True)
                match = re.search(r'(\d+)', text)
                if match:
                    snow_depth = match.group(1)
                    break

        # --- 3. TARGET LIFT DATA ---
        # Targeting the table structure from image_7a6405.jpg
        lift_table = soup.find('table', class_='normal main')
        if lift_table:
            rows = lift_table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')

                # Column 0: Lift Name | Column 2: Status Indicator
                if len(cols) >= 3:
                    name_raw = cols[0].get_text(strip=True)
                    status_raw = cols[2].get_text(strip=True)

                    # 1. Strip the "1) " prefix using regex
                    clean_name = re.sub(r'^\d+[\s\)]+', '', name_raw)
                    # 2. Create a space-less key for the map (handles "くまど ー" vs "くまどー")
                    match_key = clean_name.replace(" ", "").replace("　", "")

                    # --- STATUS LOGIC ---
                    # Using the symbols you identified: ○ = Open, × = Closed
                    is_open = any(sym in status_raw for sym in ['○', '◎', '運行中', 'OPEN'])

                    # Filter: Only add if it's one of our mapped lifts
                    if match_key in [k.replace(" ", "") for k in LIFT_NAME_MAP.keys()]:
                        # Look up English name, defaulting to clean_name if not found
                        en_name = LIFT_NAME_MAP.get(match_key, clean_name)
                        # Manual override for match_key mapping if necessary
                        for jp_key, en_val in LIFT_NAME_MAP.items():
                            if jp_key.replace(" ", "") == match_key:
                                en_name = en_val
                                break

                        lift_status_dic[en_name] = 'Open' if is_open else 'Closed'

    except Exception as e:
        print(f"AKAKURA ONSEN SCRAPE ERROR: {e}")
    finally:
        driver.quit()

    return [
        {"resort_name": "Akakura Onsen"},
        {"Summit": snow_depth, "Base": snow_depth},
        {"Base": "0"},
        lift_status_dic,
        {"last_updated": datetime.now().strftime('%Y-%m-%d %H:%M')}
    ]


if __name__ == "__main__":
    print(get_data())