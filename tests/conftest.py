import pandas as pd
import pytest
from datetime import date, time, timedelta


def _build_df(aqi_by_day):
    """Build a MultiIndexed hourly DataFrame from a list of daily AQI values."""
    dates = [date(2026, 10, 1) + timedelta(days=d) for d in range(len(aqi_by_day))]
    index = pd.MultiIndex.from_product(
        [dates, [time(h) for h in range(24)]],
        names=["date", "time"],
    )
    # Repeat each day's AQI across its 24 hours
    values = [aqi for aqi in aqi_by_day for _ in range(24)]
    return pd.DataFrame(
        {"us_aqi": values, "pm2_5": [v * 0.8 for v in values], "pm10": [v * 1.2 for v in values]},
        index=index,
    )


@pytest.fixture
def flat_df():
    """30 days of constant AQI — clean baseline for structural tests."""
    return _build_df([150] * 30)


@pytest.fixture
def improving_df():
    """22 polluted days followed by 8 clean days — trend should be IMPROVING."""
    return _build_df([200] * 22 + [100] * 8)


@pytest.fixture
def worsening_df():
    """22 clean days followed by 8 polluted days — trend should be WORSENING."""
    return _build_df([100] * 22 + [200] * 8)


@pytest.fixture
def hourly_pattern_df():
    """AQI rises with the hour of day: hour 0 is safest, hour 23 is worst."""
    dates = [date(2026, 10, 1) + timedelta(days=d) for d in range(30)]    # Creating a list of dates
    index = pd.MultiIndex.from_product(
        [dates, [time(h) for h in range(24)]], names=["date", "time"]     # Creating a dataframe with multiindex (date, time)
    )
    values = [100 + h for _ in dates for h in range(24)]     # Creating a list of values (AQI) (100, 101, 102, ...)
    return pd.DataFrame({"us_aqi": values}, index=index)