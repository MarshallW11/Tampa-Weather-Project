import requests
import pandas as pd
import psycopg2
from datetime import datetime
import os


def fetch_historical_temperatures(start_year, end_year):
    endpoint = "https://archive-api.open-meteo.com/v1/archive"
    start_date = f"{start_year}-01-01"
    end_date = f"{end_year}-12-31"

    params = {
        "latitude": 27.9506,
        "longitude": -82.4572,
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
        return df
    else:
        raise Exception(f"Error: {response.status_code}")


def insert_into_postgres(df, conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperature_data (
            date DATE PRIMARY KEY,
            temp_max FLOAT,
            temp_min FLOAT
        )
    """)
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO temperature_data (date, temp_max, temp_min)
            VALUES (%s, %s, %s)
            ON CONFLICT (date) DO NOTHING
        """, (row['date'], row['temp_max'], row['temp_min']))
    conn.commit()


if __name__ == "__main__":
    # Fetch data
    df = fetch_historical_temperatures(1965, 2023)

    # Connect to Postgres
    conn = psycopg2.connect(
        dbname="chartbrew_db",
        user="chartbrew_user",
        password="chartbrew_password",
        host="localhost",
        port="5432"
    )

    # Insert data
    insert_into_postgres(df, conn)
    conn.close()
    print("Data inserted successfully.")
