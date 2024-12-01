import requests
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from datetime import datetime


def fetch_historical_temperatures(start_year, end_year):
    endpoint = "https://archive-api.open-meteo.com/v1/archive"
    # Adjust end date to account for the 5-day delay on current data availability
    start_date = f"{start_year}-01-01"
    end_date = f"{end_year}-12-31"

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


# Fetch data for 1965–2023
df_combined = fetch_historical_temperatures(1965, 2023)

if df_combined is not None:
    # Add year column
    df_combined['year'] = df_combined['date'].dt.year

    # Calculate yearly averages for max and min temperatures
    yearly_avg = df_combined.groupby('year').agg({
        'temp_max': 'mean',
        'temp_min': 'mean'
    }).reset_index()

    # Save to CSV
    yearly_avg.to_csv('yearly_avg_temps_1965_2023.csv', index=False)

    # Plot the data
    plt.figure(figsize=(15, 7))
    plt.plot(yearly_avg['year'], yearly_avg['temp_max'], label='Average Max Temp', alpha=0.8, linewidth=2)
    plt.plot(yearly_avg['year'], yearly_avg['temp_min'], label='Average Min Temp', alpha=0.8, linewidth=2)

    plt.xlabel('Year')
    plt.ylabel('Temperature (°C)')
    plt.title('Yearly Average Temperatures (1965–2023)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('yearly_avg_temperatures_1965_2023.png', dpi=300, bbox_inches='tight')
    plt.show()

    # Print summary statistics
    avg_temp_max_c = yearly_avg['temp_max'].mean()
    avg_temp_min_c = yearly_avg['temp_min'].mean()

    print(f"Average Max Temperature (1965–2023): {avg_temp_max_c:.2f}°C")
    print(f"Average Min Temperature (1965–2023): {avg_temp_min_c:.2f}°C")
else:
    print("Failed to retrieve data.")