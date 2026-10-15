from datetime import date, datetime, time

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
def get_todays_status(df):

    row = df.iloc[-1]   # get the latest results

    aqi, pm2_5, pm10 = row.round(2)[['us_aqi', 'pm2_5', 'pm10']]

    status = get_aqi_meaning(aqi)
  
    # Now returning current data, the best format should be 
    return {'aqi' : aqi, 'pm2_5' : pm2_5, 'pm10' : pm10, 'status' : status}


# Get Historical Status
def get_historical_status(df):

  past_aqi = [df.tail(24*i)['us_aqi'].mean().round(2) for i in [3, 7, 30]]
  last_week = df.iloc[-24*14:-24*7]['us_aqi'].mean().round(2)

  if past_aqi[1] > last_week :
    quality = ((round(((past_aqi[1] - last_week) / past_aqi[1]) * 100, 2)), False)
  else :
    quality = ((round(((last_week - past_aqi[1]) / last_week) * 100, 2)), True)

  return [past_aqi, quality]

# Pattern Insights
def get_pattern_insights(df):
    """This function is gonna find the safest window and the worse window in the last week for Lahore"""

    temp = df.tail(24 * 7)['us_aqi'].groupby('time').mean().sort_values()
    lowest = temp.head(4)
    highest = temp.tail(4)

    # First converting the time to 12 Hour AM/PM format 
    lowest.index = [t.strftime('%I:%M %p') for t in lowest.index]
    highest.index = [t.strftime('%I:%M %p') for t in highest.index]

    return [lowest, highest]
    