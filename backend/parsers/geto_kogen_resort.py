from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re


def get_data():
    home_url = 'https://www.getokogen.com/winter_en/'
    op_url = 'https://www.getokogen.com/winter_en/01trail/operation.cgi'

    driver = webdriver.Chrome()
    s_depth, b_depth, fall = "0", "0", "0"

    # Initialize all lifts as 'Closed' by default
    lift_status_dic = {
        "Gondola #1": "Closed",
        "Gondola #2": "Closed",
        "Quad Lift": "Closed",
        "Pair Lift #1": "Closed",
        "Pair Lift #2": "Closed"
    }

    # MAP OF DISCOVERED OVERLAY IDs
    # Note: We need to find the IDs for Gondola #2 and Pair #2 when they open!
    ID_MAP = {
        "1619228965": "Gondola #1",
        "1619240207": "Quad Lift",
        "1618995431": "Pair Lift #1"
    }

    try:
        # --- 1. SCRAPE SNOW FROM HOMEPAGE (Your working logic) ---
        driver.get(home_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "weather_06")))
        time.sleep(2)
        home_soup = BeautifulSoup(driver.page_source, 'html.parser')

        s_div = home_soup.find('div', id='weather_05')
        b_div = home_soup.find('div', id='weather_06')
        s_depth = s_div.get_text(strip=True) if s_div else "0"
        b_depth = b_div.get_text(strip=True) if b_div else "0"

        weather_content = home_soup.find('div', class_='weather_content')
        if weather_content:
            text = weather_content.get_text()
            match = re.search(r'Last 24h/\s*(\d+)', text)
            if match: fall = match.group(1)

        # --- 2. SCRAPE LIFTS VIA PRESENCE CHECK ---
        driver.get(op_url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "course_wrapper")))
        time.sleep(3)
        op_soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Check every image on the page
        for img in op_soup.find_all('img'):
            src = img.get('src', '')
            # If any of our known 'Operating' IDs are in the filename, mark as Open
            for asset_id, lift_name in ID_MAP.items():
                if asset_id in src:
                    lift_status_dic[lift_name] = "Open"

    except Exception as e:
        print(f"SCRAPE ERROR: {e}")
    finally:
        driver.quit()

    return [
        {"resort_name": "Geto Kogen Resort"},
        {"Summit": s_depth, "Base": b_depth},
        {"Base": fall},
        lift_status_dic,
        {"last_updated": datetime.now().strftime('%Y-%m-%d %H:%M')}
    ]


if __name__ == "__main__":
    print(get_data())