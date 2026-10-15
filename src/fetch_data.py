import requests
import json
from pathlib import Path
from datetime import date, timedelta

# Open-Meteo Air Quality Endpoint
URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# How much history to fetch (analysis needs max 30 days; 60 gives headroom)
HISTORY_DAYS = 60

def fetch_and_save_data():
    """Fetch historical and current hourly air quality metrics from the Open-Meteo API
    for Lahore and cache the raw JSON response locally.

    Returns:
        dict: The raw JSON dictionary response from the API.

    Raises:
        requests.RequestException: If the network request or API call fails.
    """

    # Lahore Coordinates & Parameters
    params = {
        "latitude": 31.5204,
        "longitude": 74.3587,
        "start_date": date.today() - timedelta(days=HISTORY_DAYS),
        "end_date": date.today(),
        "hourly": "pm2_5,pm10,us_aqi",
        "timezone": "Asia/Karachi"
    }

    response = requests.get(URL, params=params, timeout=15)
    response.raise_for_status()  # Raises HTTPError if request fails
    
    data = response.json()
    
    # Save raw response to cache
    output_dir = Path(__file__).parent.parent / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)     # Instead of Raising error, it would just create the directory
    
    # Save the data in specified directory
    with open(output_dir / "lahore_aqi_raw.json", "w") as f:
        json.dump(data, f, indent=4)
    
    return data
        
# This line means that the code inside this block will only run if this script is executed directly, and not if it is imported as a module in another script.
if __name__ == "__main__":
    today = date.today()
    fetch_and_save_data(today)
    print("Successfully fetched and cached raw AQI data!")
