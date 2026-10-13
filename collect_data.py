# collect_data.py
# Pulls hourly US AQI for each city from Open-Meteo and saves it to MySQL.
# Safe to run any time: hours already saved are skipped, missed days get filled in.

import requests
from datetime import datetime
from config import CITIES, DAYS_BACK
from database import save_readings

API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

def fetch_city(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "us_aqi",
        "past_days": DAYS_BACK,
        "timezone": "Asia/Kolkata",
    }
    data = requests.get(API_URL, params=params, timeout=30).json()

    if "hourly" not in data:
        raise ValueError(data.get("reason", "no data returned"))

    now = datetime.now()
    rows = []
    for t, value in zip(data["hourly"]["time"], data["hourly"]["us_aqi"]):
        measured_at = datetime.fromisoformat(t)
        # skip missing values and future (forecast) hours
        if value is None or measured_at > now:
            continue
        rows.append((int(round(value)), measured_at))
    return rows

def collect_all_cities():
    total_new = 0
    for city, (lat, lon) in CITIES.items():
        print(f"Fetching {city}...")
        try:
            readings = fetch_city(lat, lon)
        except Exception as e:
            print(f"  SKIPPED - {e}")
            continue

        rows = [(city, aqi, measured_at) for aqi, measured_at in readings]
        new_rows = save_readings(rows)
        print(f"  {len(rows)} readings fetched, {new_rows} new")
        total_new += new_rows

    print(f"\nDone. {total_new} new readings saved.")

if __name__ == "__main__":
    collect_all_cities()