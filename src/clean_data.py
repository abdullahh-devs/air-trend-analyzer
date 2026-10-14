import pandas as pd
import json
from datetime import date, datetime

# 1. Read the JSON file using standard Python
with open('../data/raw/lahore_aqi_raw.json', 'r') as f:
    raw_data = json.load(f)

# 2. Extract ONLY the 'hourly' key where the actual data arrays live
df = pd.DataFrame(raw_data['hourly'])


# Converting 'time' string to actual time object
df['time'] = pd.to_datetime(df['time'])

df['date'] = df['time'].dt.date
df['time'] = df['time'].dt.time

df.set_index(['date', 'time'], inplace=True)

# Defining Meaning
def get_aqi_meaning(aqi_value):
    if aqi_value <= 50:
        return "Good"
    elif aqi_value <= 100:
        return "Moderate"
    elif aqi_value <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi_value <= 200:
        return "Unhealthy"
    elif aqi_value <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

# Get Current Status
def get_todays_status():
    today = date.today()
    hour = datetime.now().hour
    aqi, pm2_5, pm10 = df.loc[today].iloc[hour].round(2)[['us_aqi', 'pm2_5', 'pm10']]

    status = get_aqi_meaning(aqi)
  
    # Now returning current data, the best format should be 
    return {'aqi' : aqi, 'pm2_5' : pm2_5, 'pm10' : pm10, 'status' : status}


# Get Historical Status
def get_historical_status():

  past_aqi = [df.tail(24*i)['us_aqi'].mean().round(2) for i in [3, 7, 30]]
  last_week = df.iloc[-24*14:-24*7]['us_aqi'].mean().round(2)

  if past_aqi[1] > last_week :
    quality = ((round(((past_aqi[1] - last_week) / past_aqi[1]) * 100, 2)), True)
  else :
    quality = ((round(((last_week - past_aqi[1]) / last_week) * 100, 2)), False)

  return [past_aqi, quality]

# Pattern Insights
def get_pattern_insights():
    """This function is gonna find the safest window and the worse window in the last week for Lahore"""

    temp = df.tail(72)['us_aqi'].groupby('time').mean().sort_values()
    lowest = temp.head(4)
    highest = temp.tail(4)

    # First converting the time to 12 Hour AM/PM format 
    lowest.index = [t.strftime('%I:%M %p') for t in lowest.index]
    highest.index = [t.strftime('%I:%M %p') for t in highest.index]
    
    return [lowest.index, highest.index]
    
    
