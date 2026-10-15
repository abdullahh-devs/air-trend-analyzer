from numpy.matrixlib import defmatrix
from datetime import date, datetime, time

# Defining Meaning
def get_aqi_meaning(aqi_value):
    """Map a numerical US AQI value to its official qualitative health category.

    Args:
        aqi_value (float or int): The US AQI numerical score.

    Returns:
        str: The qualitative air quality category (e.g., 'Good', 'Moderate', 'Hazardous').
    """

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
    """Extract the most recent hourly AQI and pollutant records from the dataset.

        Args:
            df (pd.DataFrame): MultiIndexed DataFrame containing hourly air quality data.

        Returns:
            dict: A dictionary containing current 'aqi', 'pm2_5', 'pm10', and health 'status'.
        """

    row = df.iloc[-1]   # get the latest results

    aqi, pm2_5, pm10 = row.round(2)[['us_aqi', 'pm2_5', 'pm10']]

    status = get_aqi_meaning(aqi)
  
    # Now returning current data, the best format should be 
    return {'aqi' : aqi, 'pm2_5' : pm2_5, 'pm10' : pm10, 'status' : status}


# Get Historical Status
def get_historical_status(df):
    """Calculate rolling historical AQI averages and compare last week's trend.

    Args:
        df (pd.DataFrame): MultiIndexed DataFrame containing hourly air quality data.

    Returns:
        list: A two-element list containing:
            - past_aqi (list): Averages for past 3, 7, and 30 days.
            - quality (tuple): (percentage_difference, is_improved_boolean).
    """

    past_aqi = [df.tail(24*i)['us_aqi'].mean().round(2) for i in [3, 7, 30]]
    last_week = df.iloc[-24*14:-24*7]['us_aqi'].mean().round(2)

    # WORSENED (AQI went Up)
    if past_aqi[1] > last_week :
        quality = ((round(((past_aqi[1] - last_week) / last_week) * 100, 2)), False)

    # IMPROVED (AQI went Down)
    else :
        quality = ((round(((last_week - past_aqi[1]) / last_week) * 100, 2)), True)

    return [past_aqi, quality]

# Pattern Insights
def get_pattern_insights(df):
    """Identify the safest and most dangerous hourly time windows over the past week.

    Args:
        df (pd.DataFrame): MultiIndexed DataFrame containing hourly air quality data.

    Returns:
        list: A list containing two Pandas Series representing the lowest and highest AQI hours.
    """

    temp = df.tail(24 * 7)['us_aqi'].groupby('time').mean().sort_values()
    lowest = temp.head(4)
    highest = temp.tail(4)

    # First converting the time to 12 Hour AM/PM format 
    lowest.index = [t.strftime('%I:%M %p') for t in lowest.index]
    highest.index = [t.strftime('%I:%M %p') for t in highest.index]

    return [lowest, highest]
    