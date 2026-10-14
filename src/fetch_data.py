import requests
import json
from pathlib import Path

# Open-Meteo Air Quality Endpoint
URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# Lahore Coordinates & Parameters
params = {
    "latitude": 31.5204,
    "longitude": 74.3587,
    "start_date": "2026-01-01",  # Adjust dates as needed
    "end_date": "2026-10-11",
    "hourly": "pm2_5,pm10,us_aqi",
    "timezone": "Asia/Karachi"
}

def fetch_and_save_data():
    response = requests.get(URL, params=params)
    response.raise_for_status()  # Raises HTTPError if request fails
    
    data = response.json()
    
    # Save raw response to cache
    output_dir = Path("./Air Trend Analyzer/data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)     # Instead of Raising error, it would just create the directory
    
    # Save the data in specified directory
    with open(output_dir / "lahore_aqi_raw.json", "w") as f:
        json.dump(data, f, indent=4)
        
    print("Successfully fetched and cached raw AQI data!")


# This line means that the code inside this block will only run if this script is executed directly, and not if it is imported as a module in another script.
if __name__ == "__main__":
    fetch_and_save_data()