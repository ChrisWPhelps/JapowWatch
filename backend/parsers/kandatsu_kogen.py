from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re


def get_data():
    home_url = 'https://www.kandatsu.com/'
    today_url = 'https://www.kandatsu.com/today/'

    driver = webdriver.Chrome()
    snow_depth, new_snow = "0", "0"
    lift_status_dic = {}

    try:
        # --- 1. SCRAPE SNOW FROM HOMEPAGE ---
        driver.get(home_url)
        # Target the BEM-style card container identified in the inspector
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "weather-card__cols"))
        )
        time.sleep(2)
        home_soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the snow depth (積雪) and new snowfall (新雪) rows
        rows = home_soup.find_all('div', class_='weather-card__row')
        for row in rows:
            label = row.find('span', class_='weather-card__label')
            value = row.find('span', class_='weather-card__value')
            if label and value:
                label_text = label.get_text()
                # Clean value (e.g., "125 cm" -> "125")
                clean_val = re.sub(r'\D', '', value.get_text(strip=True))

                if '積雪' in label_text or 'Snowfall' in label_text:
                    snow_depth = clean_val
                elif '新雪' in label_text or 'New' in label_text:
                    new_snow = clean_val

        # --- 2. SCRAPE LIFTS FROM /TODAY/ ---
        driver.get(today_url)
        # Target the specific body ID for the lift table
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "js-lift-table-body"))
        )
        time.sleep(3)
        today_soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Select all lift rows inside the body
        lift_rows = today_soup.select('#js-lift-table-body tr.course-table__row--lift')

        for row in lift_rows:
            name_cell = row.find(['th', 'td'], class_='course-table__td--name')
            status_cell = row.find('td', class_='course-table__status')

            if name_cell and status_cell:
                # Clean the name key (e.g., "A-lift [1770]")
                name = " ".join(name_cell.get_text().split())

                # Get raw status text and CSS classes
                status_text = status_cell.get_text(strip=True)
                classes = status_cell.get('class', [])

                # BILINGUAL INDICATORS: Checks for Japanese or English 'Open' states
                # Handles scenarios where Selenium renders auto-translated text
                open_indicators = ['運行中', 'In operation', 'Operating', 'OPEN']

                # Logic: Lift is 'Open' if the 'is-open' class is present
                # OR if the status text matches our indicators
                is_open = ('is-open' in classes) or any(ind in status_text for ind in open_indicators)

                lift_status_dic[name] = 'Open' if is_open else 'Closed'

    except Exception as e:
        print(f"KANDATSU SCRAPE ERROR: {e}")
    finally:
        driver.quit()

    # --- 3. DATA CONTRACT COMPLIANCE ---
    resort_name = {"resort_name": "Kandatsu Kogen"}
    # Mapping to both Summit and Base to keep your averaging logic consistent
    depth_dic = {"Summit": snow_depth, "Base": snow_depth}
    fall_dic = {"Base": new_snow}
    last_updated = {"last_updated": datetime.now().strftime('%Y-%m-%d %H:%M')}

    return [
        resort_name,
        depth_dic,
        fall_dic,
        lift_status_dic,
        last_updated
    ]


if __name__ == "__main__":
    # Test individual output
    print(get_data())