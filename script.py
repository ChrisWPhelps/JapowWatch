import os
import sqlite3
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'japow_watch.db')

print(API_KEY)
def update_all_resorts():
    #getch every resort in db and updates weather
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        #get resorts with their coords
        cursor.execute("SELECT id, name, lat, lon FROM resorts")
        resorts = cursor.fetchall()

        print(f"Starting update for {len(resorts)} resorts...")

        for resort_id, name, lat, lon in resorts:
            #OW API for each coord i.e resort
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()

                temp = data['main']['temp']
                conditions = data['weather'][0]['description']

                #inserts in to daily_stats table in db
                cursor.execute('''
                                    INSERT INTO daily_stats (resort_id, temp_celsius, live_weather)
                                    VALUES (?, ?, ?)
                                ''', (resort_id, temp, conditions))

                print(f"{name}: {temp}°C, {conditions}")

            except Exception as e:
                print(f"Failed to update {name}: {e}")

        conn.commit()
        print("Update cycle complete.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    update_all_resorts()