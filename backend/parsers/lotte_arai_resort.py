from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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

_COOKIE_SELECTORS = [
    "button#onetrust-accept-btn-handler",
    "#onetrust-accept-btn-handler",
    "button[aria-label*='Accept']",
    "button[aria-label*='accept']",
    ".btn-cookie-accept",
    "button.btn-cookie-accept",
    "button[class*='cookie'][class*='accept']",
    "button[class*='close']",
]


def _dismiss_cookies(driver, wait_s=2):
    for sel in _COOKIE_SELECTORS:
        try:
            el = WebDriverWait(driver, wait_s).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
            )
            el.click()
            time.sleep(0.4)
            return
        except Exception:
            continue


def _scroll_for_lazy_content(driver):
    for y in (400, 1000, 1800, 2800, 4000):
        driver.execute_script(f"window.scrollTo(0, {y});")
        time.sleep(0.7)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1.2)


def _parse_lifts_from_soup(soup):
    lift_status_dic = {}
    lift_items = soup.select(".txt-data-wrap li.txt-data-item")
    if not lift_items:
        lift_items = soup.select("li.txt-data-item")

    for item in lift_items:
        name_span = item.find("span", class_=lambda c: c and "data-info" in c)
        if not name_span:
            name_span = item.select_one("span.data-info")
        status_span = item.find("span", class_=lambda c: c and "data-status" in c)
        if not status_span:
            status_span = item.select_one("span.data-status")

        if not name_span or not status_span:
            continue

        name_raw = name_span.get_text(strip=True)
        status_icon = status_span.find("i", class_=re.compile(r"ico-arai"))
        if status_icon:
            classes = status_icon.get("class", [])
            is_open = any("open" in c.lower() for c in classes)
            status = "Open" if is_open else "Closed"
        else:
            status = "Closed"

        name_en = LIFT_NAME_MAP.get(name_raw, name_raw)
        lift_status_dic[name_en] = status

    return lift_status_dic


def get_data():
    url = "https://www.lottehotel.com/arai-resort/en/snow/slopes-guide"
    opts = Options()
    opts.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=opts)
    snow_depth = "0"
    lift_status_dic = {}

    try:
        driver.set_page_load_timeout(45)
        driver.get(url)

        _dismiss_cookies(driver)
        time.sleep(0.5)

        _scroll_for_lazy_content(driver)

        WebDriverWait(driver, 25).until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.txt-data-item")),
                EC.presence_of_element_located((By.CSS_SELECTOR, ".txt-data-wrap")),
            )
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")

        snow_items = soup.find_all("li", class_=lambda c: c and "snow-item" in c)
        for item in snow_items:
            dt = item.find("dt")
            dd = item.find("dd")
            if dt and dd:
                label = dt.get_text(strip=True).lower()
                if "depth" in label or "積雪" in label:
                    value_text = dd.get_text(strip=True)
                    match = re.search(r"(\d+)", value_text)
                    if match:
                        snow_depth = match.group(1)

        lift_status_dic = _parse_lifts_from_soup(soup)

        if not lift_status_dic:
            raise RuntimeError(
                "Lotte Arai: no lift rows parsed after load (DOM change, blocking, or timeout)."
            )

    except Exception as e:
        print(f"LOTTE ARAI SCRAPE ERROR: {e}")
        raise
    finally:
        driver.quit()

    resort_name = {"resort_name": "Lotte Arai Resort"}
    depth_dic = {"Summit": snow_depth, "Base": snow_depth}
    fall_dic = {"Base": "0"}
    last_updated = {"last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")}

    return [
        resort_name,
        depth_dic,
        fall_dic,
        lift_status_dic,
        last_updated,
    ]


if __name__ == "__main__":
    print(get_data())
