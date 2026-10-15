import pytest
from datetime import datetime
from src.analyze_data import (get_aqi_meaning, get_todays_status, get_historical_status, get_pattern_insights)



# ---------- get_aqi_meaning: category boundaries ----------
@pytest.mark.parametrize("aqi, expected", [
    (0,   "Good"),
    (50,  "Good"),
    (51,  "Moderate"),
    (100, "Moderate"),
    (101, "Unhealthy for Sensitive Groups"),
    (150, "Unhealthy for Sensitive Groups"),
    (151, "Unhealthy"),
    (200, "Unhealthy"),
    (201, "Very Unhealthy"),
    (300, "Very Unhealthy"),
    (301, "Hazardous"),
    (500, "Hazardous"),
])
def test_get_aqi_meaning_boundaries(aqi, expected):
    assert get_aqi_meaning(aqi) == expected


# ---------- get_todays_status ----------
def test_todays_status_returns_last_row(flat_df):
    result = get_todays_status(flat_df)
    assert result["aqi"] == 150
    assert result["pm2_5"] == 120       # 150 * 0.8
    assert result["pm10"] == 180        # 150 * 1.2
    assert result["status"] == "Unhealthy for Sensitive Groups"

# ---------- get_historical_status ----------
def test_historical_improving(improving_df):
    past_aqi, (pct, improved) = get_historical_status(improving_df)
    assert improved is True
    assert pct > 0


def test_historical_worsening(worsening_df):
    past_aqi, (pct, improved) = get_historical_status(worsening_df)
    assert improved is False
    assert pct > 0


def test_historical_averages(flat_df):
    past_aqi, _ = get_historical_status(flat_df)
    assert past_aqi == [150.0, 150.0, 150.0]   # 3, 7, 30-day averages


# ---------- get_pattern_insights ----------
def test_pattern_finds_extreme_hours(hourly_pattern_df):
    lowest, highest = get_pattern_insights(hourly_pattern_df)
    assert len(lowest) == 4 and len(highest) == 4
    assert lowest.index[0] == "12:00 AM"   # hour 0 = safest
    assert highest.index[-1] == "11:00 PM" # hour 23 = worst
    assert lowest.iloc[0] < highest.iloc[-1]