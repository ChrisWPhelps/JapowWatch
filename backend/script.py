import os
import sqlite3
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

#pathsto the /data folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'japow_watch.db')


def get_weather_for_coords(lat, lon):
    #helper func for the export_to_json script
    if lat is None or lon is None:
        return 0.0, "unknown"

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['main']['temp'], data['weather'][0]['description']
    except Exception as e:
        print(f"Weather API Error: {e}")
        return 0.0, "unknown"


def update_all_resorts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, name, lat, lon FROM resorts")
        resorts = cursor.fetchall()

        print(f"Updating weather for {len(resorts)} resorts in DB...")

        for resort_id, name, lat, lon in resorts:
            temp, conditions = get_weather_for_coords(lat, lon)  # Use the helper

            if conditions != "unknown":
                cursor.execute('''
                    INSERT INTO daily_stats (resort_id, temp_celsius, live_weather)
                    VALUES (?, ?, ?)
                ''', (resort_id, temp, conditions))
                print(f"{name}: {temp}°C, {conditions}")

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    update_all_resorts()