from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

# --- LIFT NAME MAPPING ---
LIFT_NAME_MAP = {
    '新井ゴンドラ': 'Arai Gondola',
    '膳棚リフト': 'Zendana Lift',
    '小毛無リフト': 'Kokenashi Lift',
    '山麓第１リフト': 'Sanroku 1st Lift',
    '山麓第2リフト': 'Sanroku 2nd Lift'
}


def get_data():
    url = 'https://www.lottehotel.com/arai-resort/en/snow/slopes-guide'
    driver = webdriver.Chrome()

    snow_depth = "0"
    lift_status_dic = {}

    try:
        driver.get(url)

        # 1. DISMISS COOKIE BANNER
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='close'], .btn-cookie-accept"))
            ).click()
        except:
            pass

        # 2. TRIGGER LAZY LOADING
        # Scrolling down to the today-chips-wrap area
        driver.execute_script("window.scrollTo(0, 1800);")
        time.sleep(3)

        # 3. WAIT FOR LIFT WRAPPER
        # Waiting for the actual list items you identified
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "txt-data-item"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # --- 4. TARGET SNOW DATA (Working logic preserved) ---
        snow_items = soup.find_all('li', class_='snow-item')
        for item in snow_items:
            dt = item.find('dt')
            dd = item.find('dd')
            if dt and dd:
                label = dt.get_text(strip=True).lower()
                if 'depth' in label or '積雪' in label:
                    value_text = dd.get_text(strip=True)
                    match = re.search(r'(\d+)', value_text)
                    if match:
                        snow_depth = match.group(1)

        # --- 5. TARGET LIFT STATUS (Path: span.data-info / span.data-status) ---
        # Based on your path: txt-data-wrap -> ul.txt-data-list -> li.txt-data-item
        wrap = soup.find('div', class_='txt-data-wrap')
        if wrap:
            lift_items = wrap.find_all('li', class_='txt-data-item')

            for item in lift_items:
                # Identifying the name in span class="data-info"
                name_span = item.find('span', class_='data-info')
                # Identifying the status in span class="data-status"
                status_span = item.find('span', class_='data-status')

                if name_span and status_span:
                    name_raw = name_span.get_text(strip=True)

                    # Look for the icon tag <i> inside the status span
                    status_icon = status_span.find('i', class_=re.compile(r'ico-arai'))

                    if status_icon:
                        classes = status_icon.get('class', [])
                        # "ico-arai-open" = Open, anything else = Closed
                        is_open = any('open' in c.lower() for c in classes)
                        status = 'Open' if is_open else 'Closed'
                    else:
                        status = 'Closed'

                    # Map to English if Japanese is returned
                    name_en = LIFT_NAME_MAP.get(name_raw, name_raw)
                    lift_status_dic[name_en] = status

    except Exception as e:
        print(f"LOTTE ARAI SCRAPE ERROR: {e}")
    finally:
        driver.quit()

    # --- 6. DATA CONTRACT COMPLIANCE ---
    resort_name = {"resort_name": "Lotte Arai Resort"}
    depth_dic = {"Summit": snow_depth, "Base": snow_depth}
    fall_dic = {"Base": "0"}
    last_updated = {"last_updated": datetime.now().strftime('%Y-%m-%d %H:%M')}

    return [
        resort_name,
        depth_dic,
        fall_dic,
        lift_status_dic,
        last_updated
    ]


if __name__ == "__main__":
    print(get_data())