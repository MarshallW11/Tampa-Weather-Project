import requests
import pandas as pd
from datetime import datetime, timedelta


def fetch_historical_temperatures(year):
    endpoint = "https://archive-api.open-meteo.com/v1/archive"
    # Adjust end date to account for the 5-day delay on current data availability
    today = datetime.now()
    end_date = min(today - timedelta(days=5), datetime(year, 12, 31)).strftime("%Y-%m-%d")
    start_date = f"{year}-01-01"

    params = {
        "latitude": 27.9506,  # Tampa Bay latitude
        "longitude": -82.4572,  # Tampa Bay longitude
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "America/New_York"
    }

    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        dates = data['daily']['time']
        temps_max = data['daily']['temperature_2m_max']
        temps_min = data['daily']['temperature_2m_min']
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'temp_max': temps_max,
            'temp_min': temps_min
        })
        df['temp_avg_c'] = (df['temp_max'] + df['temp_min']) / 2  # Average temperature in Celsius
        df['temp_avg_f'] = (df['temp_avg_c'] * 9 / 5) + 32  # Convert to Fahrenheit
        return df
    else:
        print(f"Error: {response.status_code}")
        return None


# Fetch historical data for both 2023 and available data in 2024
df_2023 = fetch_historical_temperatures(2023)
df_2024 = fetch_historical_temperatures(2024)

# Calculate the average temperatures if data exists for both years
if df_2023 is not None and df_2024 is not None:
    # Calculate average temperatures in Celsius
    avg_temp_2023_c = df_2023['temp_avg_c'].mean()
    avg_temp_2024_c = df_2024['temp_avg_c'].mean()

    # Calculate average temperatures in Fahrenheit
    avg_temp_2023_f = df_2023['temp_avg_f'].mean()
    avg_temp_2024_f = df_2024['temp_avg_f'].mean()

    # Calculate the temperature change
    temp_change_c = avg_temp_2024_c - avg_temp_2023_c
    temp_change_f = avg_temp_2024_f - avg_temp_2023_f

    # Print the results
    print(f"Average temperature in 2023: {avg_temp_2023_c:.2f}°C / {avg_temp_2023_f:.2f}°F")
    print(f"Average temperature in 2024: {avg_temp_2024_c:.2f}°C / {avg_temp_2024_f:.2f}°F")
    print(f"Average temperature change from 2023 to 2024: {temp_change_c:.2f}°C / {temp_change_f:.2f}°F")
else:
    print("Data retrieval failed for one or both years.")
