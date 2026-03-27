import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_data():
    driver = webdriver.Chrome()
    driver.get('https://furapuri.com/ski/')

    # Wait until the info table is rendered (Vue app hydrates the DOM)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.info table tbody tr"))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # ── Lift status ──────────────────────────────────────────────────────────
    # Each <tr> (skipping the header row class="head") contains:
    #   <td>zone letter</td>
    #   <td><div class="en">Lift Name</div></td>
    #   <td><div class="en">OPEN/CLOSED</div></td>
    #   <td>...</td>  (extra info, ignored)
    lgrs_div = soup.find("div", class_="lgrs")

    lift_dic = {}
    if lgrs_div:
        rows = lgrs_div.find_all("tr")
        for row in rows:
            # Skip the header row
            if "head" in (row.get("class") or []):
                continue

            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            # Name: the English div inside the second cell
            name_div = cells[1].find("div", class_="en")
            # Status: the English div inside the third cell
            status_div = cells[2].find("div", class_="en")

            if name_div and status_div:
                name   = name_div.get_text(strip=True)
                status = status_div.get_text(strip=True)
                if status == "OPEN":
                    status = "Open"
                else:
                    status = "Closed"
                if name:
                    lift_dic[name] = status

    # ── Top snowbase ─────────────────────────────────────────────────────────
    # From the screenshot: the info > table contains rows with values like
    # 5m/s · 0cm · 180cm · 0℃  — the 180cm cell is the top snowbase
    info_div = soup.find("div", class_="info")
    last_snowfall_cm = None
    top_snowbase_cm  = None

    if info_div:
        table = info_div.find("table")
        if table:
            for row in table.find_all("tr"):
                cm_values = []
                for td in row.find_all("td"):
                    m = re.fullmatch(r'(\d+)cm', td.get_text(strip=True))
                    if m:
                        cm_values.append(int(m.group(1)))
                # We expect exactly 2 cm cells per data row: snowfall then snowbase
                if len(cm_values) >= 2:
                    last_snowfall_cm = cm_values[0]
                    top_snowbase_cm  = cm_values[1]
                    break  # first matching data row is enough

    # ── Assemble final result ────────────────────────────────────────────────
    resort_name  = {"resort_name": "Furapuri Ski Resort"}
    last_updated = {"last_updated": datetime.now().strftime('%Y-%m-%d %H:%M')}
    snowbase     = {"Furano": top_snowbase_cm}
    snowfall = {"Furano": last_snowfall_cm}

    final_return = [
        resort_name,
        snowbase,
        snowfall,
        lift_dic,
        last_updated,
    ]

    return final_return

print (get_data())
