import pandas as pd
import pytest
from datetime import time

from main import group_into_ranges, fmt_hour, fmt_range, format_window


# ---------- group_into_ranges ----------
def test_consecutive_hours():
    assert group_into_ranges([13, 14, 15, 16]) == [(13, 16)]


def test_scattered_hours():
    assert group_into_ranges([14, 15, 22, 23]) == [(14, 15), (22, 23)]


def test_midnight_wrap():
    # 11 PM, 12 AM, 1 AM -> ONE range across midnight
    assert group_into_ranges([23, 0, 1]) == [(23, 25)]


def test_single_hour():
    assert group_into_ranges([10]) == [(10, 10)]


# ---------- formatting helpers ----------
@pytest.mark.parametrize("hour, expected", [
    (0,  "12:00 AM"),
    (12, "12:00 PM"),
    (13, "1:00 PM"),
    (23, "11:00 PM"),
])
def test_fmt_hour(hour, expected):
    assert fmt_hour(hour) == expected


def test_fmt_range_single():
    assert fmt_range((10, 10)) == "10:00 AM"


def test_fmt_range_span():
    assert fmt_range((14, 16)) == "2:00 PM - 4:00 PM"


# ---------- format_window ----------
def test_format_window_scattered():
    # Safest hours are 2 PM, 3 PM, 10 PM, 11 PM (non-consecutive!)
    s = pd.Series(
        [160, 165, 200, 205],
        index=["2:00 PM", "3:00 PM", "10:00 PM", "11:00 PM"],
    )
    window, avg = format_window(s)
    assert window == "2:00 PM - 3:00 PM, 10:00 PM - 11:00 PM"
    assert avg == 182   # round(mean of AQI, actual value is 182.5 but Python's round will round it to nearest even number)