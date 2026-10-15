from datetime import timedelta
import requests
import argparse
import json
import pandas as pd
from datetime import datetime, date
from pathlib import Path
import sys
import os

from src.analyze_data import get_todays_status, get_historical_status, get_pattern_insights
from src.fetch_data import fetch_and_save_data

DATA_PATH = Path(__file__).parent / "data" / "raw" / "lahore_aqi_raw.json"
# Save the cleaned, analysis-ready dataset
CLEAN_PATH = Path(__file__).parent / "data" / "processed" / "lahore_aqi_clean.csv"
CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)

# ---------- ANSI Color Codes ----------
class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    ORANGE = "\033[38;5;208m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    HEADING = "\033[1m"

def status_color(status):
    """Pick a color based on AQI category."""
    return {
        "Good": Color.GREEN,
        "Moderate": Color.YELLOW,
        "Unhealthy for Sensitive Groups": Color.ORANGE,
        "Unhealthy": Color.ORANGE,
        "Very Unhealthy": Color.RED,
        "Hazardous": Color.RED,
    }.get(status, Color.RESET)          # .get(key, default)

# ---------- Time Window Helpers ----------
def group_into_ranges(hours):
    """Group sorted hour numbers into consecutive ranges.
    Handles the midnight wrap (e.g., 23 and 0 are consecutive)."""
    hours = sorted(set(hours))     # set removes any duplicate
    ranges = []
    start = prev = hours[0]
    for h in hours[1:]:
        if h == prev + 1:           # Check for consecutive range
            prev = h                    # If found then update prev for next consecutive range
        else:
            ranges.append((start, prev))       # Else save the past ranges
            start = prev = h            # And Update prev/start for check next consecutive range

    # Appending last range
    ranges.append((start, prev))

    # Handling the midnight wrap (23 and 0 are continuous!)
    if len(ranges) > 1 and ranges[0][0] == 0 and ranges[-1][1] == 23:
        first = ranges.pop(0)
        last = ranges.pop()
        ranges.append((last[0], first[1] + 24))

    # Return the final range
    return ranges   

def fmt_hour(h):
    """Convert 0-23 hour to 12-hour format (e.g. 13 -> "01:00 PM")."""
    h = h % 24
    return f"{h % 12 or 12}:00 {'AM' if h < 12 else 'PM'}"

def fmt_range(r):
    """Convert a range of hours into a readable format (e.g. (0, 2) -> "12:00 AM - 02:00 AM")."""

    # unpack the tuple
    start, end = r
    # if the range is just one hour
    if start == end:
        return fmt_hour(start)
    # otherwise return the range
    return f"{fmt_hour(start)} - {fmt_hour(end)}"

def format_window(series):
    """Turn a time-indexed AQI series into (readable window string, avg AQI)."""
    hours = [datetime.strptime(t, "%I:%M %p").hour for t in series.index]
    ranges = group_into_ranges(hours)       # Group int hours into ranges (tuples)
    window = ", ".join(fmt_range(r) for r in ranges)      # Formating the hour ranges
    avg = round(series.mean())          # Get the Average AQI of given 4 hours
    return window, avg

def load_raw_data(offline=False):

    if not offline:
        try :
            return fetch_and_save_data(date.today()), True
        except requests.RequestException as e :
            print(f"{Color.YELLOW}[!] API unreachable ({type(e).__name__}) \n - Falling back to cached data...{Color.RESET}\n")
    
    if not DATA_PATH.exists():
        sys.exit(f"[X] No internet connection and no cached data found. Aborting.")
    
    with open(DATA_PATH, 'r') as f:
        return json.load(f), False


# ---------- Report Printer ----------
def print_report(current, historical, patterns, hours_offset, width=None):

    if width is None:
        try:
            width = int(os.get_terminal_size().columns * 0.75)
        except:
            width = 70

    now = datetime.now() - timedelta(hours=hours_offset)

    print("=" * width)
    print(f"{Color.BOLD}{Color.HEADING}   LAHORE AIR QUALITY REPORT{Color.RESET}".center(width))
    print("=" * width)
    print()

    # [CURRENT STATUS]
    print(f"{Color.BOLD}[CURRENT STATUS]{Color.RESET} ({now.strftime('%Y-%m-%d %H:%M')})")
    c = status_color(current['status'])
    print(f" - US AQI : {c}{Color.BOLD}{current['aqi']:.0f} [{current['status'].upper()}]{Color.RESET}")
    print(f" - PM2.5  : {current['pm2_5']} µg/m³")
    print(f" - PM10   : {current['pm10']} µg/m³")
    print()

    # [HISTORICAL TRENDS]
    past_aqi, (pct, improved) = historical
    print(f"{Color.BOLD}[HISTORICAL TRENDS]{Color.RESET}")
    labels = ["Past 3 Days Avg ", "Past 7 Days Avg ", "Past 30 Days Avg"]
    for label, val in zip(labels, past_aqi):
        print(f" - {label}: {val:.0f} AQI")
    if improved:
        trend = (f"{Color.GREEN}Trend: Air quality has {Color.BOLD}IMPROVED "
                 f"by {pct}%{Color.RESET}{Color.GREEN} over the last week.{Color.RESET}")
    else:
        trend = (f"{Color.ORANGE}Trend: Air quality has {Color.BOLD}WORSENED "
                 f"by {pct}%{Color.RESET}{Color.ORANGE} over the last week.{Color.RESET}")
    print(f" -> {trend}")
    print()

    # [PATTERN INSIGHTS]
    print(f"{Color.BOLD}[PATTERN INSIGHTS]{Color.RESET}")
    safe_window, safe_avg = format_window(patterns[0])
    peak_window, peak_avg = format_window(patterns[1])
    print(f" - Safest Window : {Color.GREEN}{safe_window}{Color.RESET} (Avg AQI: {safe_avg})")
    print(f" - Peak Danger   : {Color.RED}{peak_window}{Color.RESET} (Avg AQI: {peak_avg})")
    print()

    print("=" * width)


# ---------- Main ----------
if __name__ == "__main__":

    # Adding Command Line Arguments (help and offline mode)
    parser = argparse.ArgumentParser(description="Lahore Air Quality Report Generator")
    parser.add_argument('--offline', action='store_true', help="Skip the API call and analyze cached data.")
    args = parser.parse_args()

    raw_data, fresh = load_raw_data(offline=args.offline)

    hours_old = 0
    if not fresh:
        age = datetime.now() - datetime.fromtimestamp(DATA_PATH.stat().st_mtime)
        hours_old = round(age.total_seconds() / 3600, 2)
        print(f"{Color.YELLOW}[Offline Mode] Using data cached {hours_old} hours ago. \nCurrent reading reflects the last available hour. {Color.RESET}\n")
        
    # Converting the data into a Pandas DataFrame
    df = pd.DataFrame(raw_data['hourly'])   

    # Converting the time into a datetime object and spliting that to two columns
    df['time'] = pd.to_datetime(df['time'])
    df['date'] = df['time'].dt.date
    df['time'] = df['time'].dt.time
    df.set_index(['date', 'time'], inplace=True)

    # Saving the Data into CSV as processed data
    df.to_csv(CLEAN_PATH)
    
    # Get the processed information
    current = get_todays_status(df)
    historical = get_historical_status(df)
    patterns = get_pattern_insights(df)

    # Printing the Report
    print_report(current, historical, patterns, hours_old)