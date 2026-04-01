"""
Kiroro Snow World — single HTTP fetch to dashboard; parse snow table + lift lines from HTML/text.
Refine regex/DOM if Kiroro changes layout.
"""
from __future__ import annotations

import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup, NavigableString

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JapowWatch/1.0; +https://example.invalid)"}
DASHBOARD_URL = "https://www.kiroro.co.jp/dashboard/"


def _normalize_lift_status(line: str) -> str:
    if "Operating" in line or "operating" in line:
        return "Open"
    if "Suspended" in line or "suspended" in line:
        return "Closed"
    if "Closed" in line or "closed" in line:
        return "Closed"
    return "Closed"


def _parse_snow_from_soup(soup: BeautifulSoup) -> tuple[dict[str, str], dict[str, str]]:
    """Peak/Base depth and 24h snowfall from weather table rows."""
    snow_depth = {"Peak": "0", "Base": "0"}
    new_snow = {"24h": "0"}

    for row in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
        if len(cells) < 2:
            continue
        label = cells[0].lower()
        if "snow depth" in label and len(cells) >= 3:
            mp = re.search(r"(\d+)", cells[1])
            mb = re.search(r"(\d+)", cells[2])
            if mp and mb:
                snow_depth["Peak"], snow_depth["Base"] = mp.group(1), mb.group(1)
        if "snowfall in last 24" in label or ("24" in label and "snowfall" in label):
            m = re.search(r"(\d+)", cells[1]) if len(cells) > 1 else None
            if m:
                new_snow["24h"] = m.group(1)

    return snow_depth, new_snow


def _parse_snow_from_text(text: str) -> tuple[dict[str, str], dict[str, str]]:
    """Fallback when table markup differs (pipe-separated markdown-style copy)."""
    snow_depth = {"Peak": "0", "Base": "0"}
    new_snow = {"24h": "0"}

    compact = re.sub(r"\s+", " ", text)
    m = re.search(
        r"Snow Depth\s*\|\s*(\d+)\s*cm\s*\|\s*(\d+)\s*cm",
        compact,
        flags=re.IGNORECASE,
    )
    if m:
        snow_depth["Peak"], snow_depth["Base"] = m.group(1), m.group(2)

    m2 = re.search(
        r"Snowfall in last 24 hours\s*\|\s*(\d+)\s*cm",
        compact,
        flags=re.IGNORECASE,
    )
    if m2:
        new_snow["24h"] = m2.group(1)

    if snow_depth == {"Peak": "0", "Base": "0"}:
        m3 = re.search(
            r"Snowfall\s*\(cm\).*?(\d+)\s*Peak.*?(\d+)\s*Base",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if m3:
            snow_depth["Peak"], snow_depth["Base"] = m3.group(1), m3.group(2)

    return snow_depth, new_snow


def _parse_lifts_from_dashboard_text(text: str) -> dict[str, str]:
    """Parse 'NameOperating …' / 'NameSuspended' lines under Lift Status (dashboard copy)."""
    lifts: dict[str, str] = {}
    lower = text.lower()
    start = lower.rfind("lift status")
    if start == -1:
        return lifts
    end = lower.find("tree run", start + 1)
    chunk = text[start:end] if end != -1 else text[start : start + 5000]

    for line in chunk.splitlines():
        line = line.strip()
        if len(line) < 8:
            continue
        m = re.match(
            r"^(.+?)\s+(Operating(?:\s+.+)?|Suspended|Closed)\b",
            line,
            flags=re.IGNORECASE,
        )
        if not m:
            continue
        name = m.group(1).strip()
        status_bit = m.group(2)
        if len(name) > 120 or not name:
            continue
        lifts[name] = _normalize_lift_status(status_bit)

    return lifts


def _parse_lifts_from_soup(soup: BeautifulSoup) -> dict[str, str]:
    """Prefer plain-text lift lines; DOM boxes are a fallback when layout matches."""
    text = soup.get_text("\n", strip=True)
    lifts = _parse_lifts_from_dashboard_text(text)
    if lifts:
        return lifts

    status_table = soup.find("div", class_=re.compile(r"operation-status.*lift", re.I))
    if not status_table:
        return {}
    inner = status_table.find("div", class_=re.compile(r"operation-status__inner", re.I))
    if not inner:
        return {}
    out: dict[str, str] = {}
    for box in inner.find_all("div", recursive=True):
        span = box.find("span")
        if not span:
            continue
        name = None
        for child in box.children:
            if isinstance(child, NavigableString):
                s = str(child).strip().strip('"')
                if s:
                    name = s
                    break
        if not name:
            continue
        out[name] = _normalize_lift_status(span.get_text())
    return out


def _parse_lifts_from_text_fallback(text: str) -> dict[str, str]:
    """Line-based fallback when DOM classes change."""
    lifts: dict[str, str] = {}
    lower = text.lower()
    start = lower.find("lift status")
    end = lower.find("tree run", start + 1)
    chunk = text[start:end] if start != -1 and end != -1 else text
    for line in chunk.splitlines():
        line = line.strip()
        if "Operating" in line and len(line) > 5:
            parts = line.split("Operating", 1)
            if parts[0].strip():
                lifts[parts[0].strip()] = "Open"
        elif "Suspended" in line:
            parts = line.split("Suspended", 1)
            if parts[0].strip():
                lifts[parts[0].strip()] = "Closed"
    return lifts


def get_data():
    last_updated = {"last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")}

    r = requests.get(DASHBOARD_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")
    body_text = soup.get_text("\n", strip=True)

    snow_depth, new_snow = _parse_snow_from_soup(soup)
    if snow_depth == {"Peak": "0", "Base": "0"}:
        sd2, ns2 = _parse_snow_from_text(body_text)
        snow_depth, new_snow = sd2, ns2
    lift_dic = _parse_lifts_from_soup(soup)
    if not lift_dic:
        lift_dic = _parse_lifts_from_text_fallback(body_text)
    if not lift_dic:
        lift_dic = _parse_lifts_from_dashboard_text(body_text)

    if not lift_dic:
        raise RuntimeError("Kiroro: could not parse any lifts from dashboard HTML")

    return [
        {"resort_name": "Kiroro Snow World"},
        snow_depth,
        new_snow,
        lift_dic,
        last_updated,
    ]


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_data())
