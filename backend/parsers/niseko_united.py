"""
Niseko United — 5-slot scraper contract.
Single Selenium load of https://www.niseko.ne.jp/en/niseko-lift-status/ :

  - Snow / 24h: #liftWeatherArea → ul → li columns (h3 = area name). Each column has
    h4 sections for peak/base (Japanese 山頂・山麓 and/or English Mountain peak/base).
    Metrics: prefer ul > li[1] / li[2]; fallback to <p> lines matching hardcoded JP+EN labels.
  - Lifts: #liftStatusArea (unchanged).

Does not use browser locale; only explicit label fragments the site is known to emit.
"""
from __future__ import annotations

import re
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

LIFT_URL = "https://www.niseko.ne.jp/en/niseko-lift-status/"

# Bilingual whitelist: section headings (h4 text may be JP-only, EN-only, or mixed)
_PEAK_MARKERS_JP = ("山頂",)
_BASE_MARKERS_JP = ("山麓",)
_PEAK_MARKERS_EN = ("mountain peak",)
_BASE_MARKERS_EN = ("mountain base",)

# Bilingual whitelist: snow depth line inside <p> or <li> text
_DEPTH_LABEL_MARKERS = (
    "積雪深",
    "snow base(cm)",
    "snow depth",
)
# 24h snowfall line
_SNOW24_LABEL_MARKERS = (
    "24時間積雪量",
    "24hrs snowfall",
    "24 hour snowfall",
    "24-hour snowfall",
    "24hrs snow",
)


def _heading_is_peak(label: str) -> bool:
    t = (label or "").strip()
    if any(m in t for m in _PEAK_MARKERS_JP):
        return True
    low = t.lower()
    return any(m in low for m in _PEAK_MARKERS_EN)


def _heading_is_base(label: str) -> bool:
    t = (label or "").strip()
    if any(m in t for m in _BASE_MARKERS_JP):
        return True
    low = t.lower()
    return any(m in low for m in _BASE_MARKERS_EN)


def _normalize_lift_status(raw: str) -> str:
    t = (raw or "").strip()
    if not t or t == "-":
        return "Closed"
    u = t.upper()
    if "OPERATING" in u or "OPEN" in u:
        return "Open" if "SLOW" not in u and "SUSPEND" not in u else "Operating"
    if "SUSPEND" in u or "STANDBY" in u:
        return "Closed"
    if "CLOSE" in u:
        return "Closed"
    return t


def _extract_cm_digits(p_text: str) -> str:
    m = re.search(r"(\d+)", p_text or "")
    return m.group(1) if m else "0"


def _metrics_from_ul(ul) -> tuple[str, str] | None:
    lis = ul.find_all("li", recursive=False)
    if len(lis) < 3:
        return None
    depth_line = lis[1].get_text(" ", strip=True)
    snow24_line = lis[2].get_text(" ", strip=True)
    return _extract_cm_digits(depth_line), _extract_cm_digits(snow24_line)


def _metrics_from_p_tags(scope) -> tuple[str, str]:
    """Find depth / 24h by explicit JP+EN substrings in descendant <p>."""
    depth_val, snow24_val = "0", "0"
    for p in scope.find_all("p"):
        t = p.get_text(" ", strip=True)
        low = t.lower()
        if "積雪深" in t or any(m in t for m in _DEPTH_LABEL_MARKERS if not m.isascii()):
            depth_val = _extract_cm_digits(t)
        elif any(m in low for m in ("snow base", "snow depth")):
            depth_val = _extract_cm_digits(t)

        if any(m in t for m in _SNOW24_LABEL_MARKERS if not m.isascii()):
            snow24_val = _extract_cm_digits(t)
        elif any(m in low for m in ("24hrs snowfall", "24 hour snowfall", "24-hour snowfall")):
            snow24_val = _extract_cm_digits(t)
    return depth_val, snow24_val


def _parse_lift_weather_area(soup: BeautifulSoup) -> tuple[dict[str, str], dict[str, str]]:
    snow_depth: dict[str, str] = {}
    new_snow: dict[str, str] = {}

    container = soup.find("div", id="liftWeatherArea")
    if not container:
        return {"Peak": "0", "Base": "0"}, {"24h": "0"}

    # Primary: first ul whose direct children are column lis with h3
    main_ul = None
    for ul in container.find_all("ul"):
        for li in ul.find_all("li", recursive=False):
            if li.find("h3"):
                main_ul = ul
                break
        if main_ul:
            break

    if not main_ul:
        return {"Peak": "0", "Base": "0"}, {"24h": "0"}

    for li in main_ul.find_all("li", recursive=False):
        h3 = li.find("h3", recursive=False)
        if not h3:
            continue
        area = h3.get_text(strip=True)
        if not area:
            continue

        for h4 in li.find_all("h4"):
            label = h4.get_text(strip=True)
            if _heading_is_peak(label):
                section = "Peak"
            elif _heading_is_base(label):
                section = "Base"
            else:
                continue

            parent = h4.parent
            if not parent:
                continue

            ul_metrics = parent.find("ul")
            if not ul_metrics:
                ul_metrics = h4.find_next_sibling("ul")

            d, s24 = "0", "0"
            if ul_metrics:
                got = _metrics_from_ul(ul_metrics)
                if got:
                    d, s24 = got
                else:
                    d, s24 = _metrics_from_p_tags(parent)
            else:
                d, s24 = _metrics_from_p_tags(parent)

            key_depth = f"{area} | {section}"
            snow_depth[key_depth] = d
            new_snow[f"{area} | {section} 24h"] = s24

    if not snow_depth:
        return {"Peak": "0", "Base": "0"}, {"24h": "0"}

    return snow_depth, new_snow


def _parse_lifts_from_soup(soup: BeautifulSoup) -> dict[str, str]:
    """Flat 'Area | Lift' → status from #liftStatusArea."""
    lift_status_area = soup.find("div", id="liftStatusArea")
    if not lift_status_area:
        return {}

    flat: dict[str, str] = {}
    resort_lis = lift_status_area.find_all(
        "li", id=lambda x: x and str(x).startswith("liftList_tag_")
    )

    for resort_li in resort_lis:
        h3 = resort_li.find("h3")
        area = h3.get_text(strip=True) if h3 else "Unknown"
        for ul in resort_li.find_all("ul", id=True):
            if "liftListHeader" in (ul.get("class") or []):
                continue
            lis = ul.find_all("li", recursive=False)
            if len(lis) < 3:
                continue
            lift_name = lis[0].get_text(strip=True)
            if not lift_name:
                continue
            status_el = lis[2]
            if status_el.find("img", class_="liftStatusPic"):
                status_raw = "-"
            else:
                status_raw = status_el.get_text(strip=True) or "-"
            key = f"{area} | {lift_name}"
            flat[key] = _normalize_lift_status(status_raw)

    return flat


def _weather_area_populated(driver) -> bool:
    """True when liftWeatherArea has JP/EN snow labels or a cm depth (post-JS fill)."""
    try:
        el = driver.find_element(By.ID, "liftWeatherArea")
        html = el.get_attribute("innerHTML") or ""
    except Exception:
        return False
    low = html.lower()
    if "積雪深" in html:
        return True
    if "snow base" in low and "cm" in low:
        return True
    if re.search(r"\d+\s*</p>\s*</li>", html):  # loose: digits in list item
        return True
    if re.search(r"\d+\s*cm", html, re.I):
        return True
    return False


def _fetch_niseko_soup() -> BeautifulSoup:
    """One browser session: wait for weather content + lift DOM, return parsed HTML."""
    driver = webdriver.Chrome()
    try:
        driver.get(LIFT_URL)
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.ID, "liftWeatherArea"))
        )
        WebDriverWait(driver, 25).until(lambda d: _weather_area_populated(d))
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#liftStatusArea ul[id] > li p")
            )
        )
        return BeautifulSoup(driver.page_source, "html.parser")
    finally:
        driver.quit()


def get_data():
    last_updated = {"last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")}
    soup = _fetch_niseko_soup()
    snow_depth, new_snow = _parse_lift_weather_area(soup)
    lift_flat = _parse_lifts_from_soup(soup)

    return [
        {"resort_name": "Niseko United"},
        snow_depth,
        new_snow,
        lift_flat,
        last_updated,
    ]


if __name__ == "__main__":
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    from pprint import pprint

    pprint(get_data())
