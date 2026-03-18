import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'japow_watch.db')
OUTPUT_FILE = os.path.join(BASE_DIR, 'resort_data.json')


def export_latest_data():
    conn = sqlite3.connect(DB_PATH)
    # what row factory is: https://stackoverflow.com/questions/44009452/what-is-the-purpose-of-the-row-factory-method-of-an-sqlite3-connection-object
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    #queries for most recent daily_stats entry for every resort
    query = '''
        SELECT 
            r.name, 
            r.region, 
            r.prefecture, 
            r.lat, 
            r.lon, 
            r.url,
            d.temp_celsius, 
            d.snow_depth_cm, 
            d.lift_status, 
            d.live_weather,
            d.timestamp
        FROM resorts r
        LEFT JOIN daily_stats d ON r.id = d.resort_id
        WHERE d.id = (
            SELECT MAX(id) 
            FROM daily_stats 
            WHERE resort_id = r.id
        ) OR d.id IS NULL
    '''

    try:
        cursor.execute(query)
        rows = cursor.fetchall()

        #convert .Row objects to a list of dictionaries
        resort_list = []
        for row in rows:
            resort_dict = dict(row)

            # CRITICAL: Parse the lift_status string back into a JSON array
            # This ensures the frontend sees a literal list, not a escaped string.
            if resort_dict['lift_status']:
                try:
                    resort_dict['lift_status'] = json.loads(resort_dict['lift_status'])
                except (json.JSONDecodeError, TypeError):
                    # Fallback if the data is corrupted or in the old format
                    resort_dict['lift_status'] = None

            resort_list.append(resort_dict)

        with open(OUTPUT_FILE, 'w') as f:
            json.dump(resort_list, f, indent=4)

        print(f"SUCCESS: Exported {len(resort_list)} resorts to {OUTPUT_FILE}")

    except sqlite3.Error as e:
        print(f"DATABASE ERROR: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    export_latest_data()