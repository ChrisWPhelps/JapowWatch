"""Unit tests for parsers.snow_contract (no network, no JSON artifacts)."""

import copy

import pytest

from parsers.snow_contract import (
    DASH_PLACEHOLDERS,
    normalize_depth_value,
    normalize_scraper_result,
    normalize_snow_dict,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        (None, "0"),
        ("", "0"),
        ("  ", "0"),
        ("-", "0"),
        ("–", "0"),
        ("―", "0"),
        ("120", "120"),
        (" 120 ", "120"),
        ("120cm", "120"),
        (" 90cm ", "90"),
        ("abc", "0"),
        ("12a", "0"),
        (0, "0"),
        (155, "155"),
        (155.0, "155"),
        (155.5, "0"),
        (True, "0"),
        (False, "0"),
    ],
)
def test_normalize_depth_value(raw, expected):
    assert normalize_depth_value(raw) == expected


def test_dash_placeholders_cover_unicode_dashes():
    for ch in DASH_PLACEHOLDERS:
        assert normalize_depth_value(ch) == "0"


def test_normalize_snow_dict():
    d = {"Base": "-", "Peak": "90"}
    assert normalize_snow_dict(d) == {"Base": "0", "Peak": "90"}


def test_normalize_snow_dict_non_dict_passthrough():
    assert normalize_snow_dict("x") == "x"


def test_normalize_scraper_result_none():
    assert normalize_scraper_result(None) is None


def test_normalize_scraper_result_short_list_unchanged():
    assert normalize_scraper_result([]) == []
    assert normalize_scraper_result([{}, {}]) == [{}, {}]


def test_normalize_scraper_result_mutates_snow_slots():
    row = [
        {"resort_name": "Test"},
        {"a": "-", "b": "10"},
        {"c": "5cm"},
        {"lift": "Open"},
        {"last_updated": "2026-01-01 12:00"},
    ]
    backup = copy.deepcopy(row)
    normalize_scraper_result(row)
    assert row[0] == backup[0]
    assert row[1] == {"a": "0", "b": "10"}
    assert row[2] == {"c": "5"}
    assert row[3] == backup[3]
    assert row[4] == backup[4]
