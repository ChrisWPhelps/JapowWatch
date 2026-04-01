import json
import sqlite3
import os
from datetime import datetime
from script import get_weather_for_coords

def export_json():
    #loads raw scraper data from the backend/data subfolder
    try:
        input_file = os.path.join('data', 'scraper_results.json')
        with open(input_file, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Run crawler.py first.")
        return

    #connect to DB to get static data
    db_path = os.path.join('data', 'japow_watch.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    #mapp DB names to the static data
    cursor.execute("SELECT name, region, prefecture, lat, lon, url FROM resorts")
    meta_rows = cursor.fetchall()
    resort_meta = {row[0]: {
        "region": row[1],
        "prefecture": row[2],
        "lat": row[3],
        "lon": row[4],
        "url": row[5]
    } for row in meta_rows}

    final_output = []

    #Scraper data -> frontend schema
    print(f"Updating {len(scraped_data)} resorts with weather data.")

    for resort_list in scraped_data:
        name_dict = resort_list[0]
        snow_dict = resort_list[1]
        lift_dict = resort_list[3]

        resort_name = name_dict['resort_name']
        meta = resort_meta.get(resort_name, {})

        #Weather: API pull-uses coords from the DB lookup to get live.
        live_temp, weather_desc = get_weather_for_coords(meta.get("lat"), meta.get("lon"))

        #Snow avg: Avg of peak/base or summit/mid/base, etc... just gives a single int
        depths = [int(v) for v in snow_dict.values() if str(v).isdigit()]
        avg_snow = sum(depths) // len(depths) if depths else 0

        #map into array of objs
        formatted_lifts = [
            {"name": lift_name, "status": status}
            for lift_name, status in lift_dict.items()
        ]

        # Match the format to match the object we agreed on.
        resort_obj = {
            "name": resort_name,
            "region": meta.get("region"),
            "prefecture": meta.get("prefecture"),
            "lat": meta.get("lat"),
            "lon": meta.get("lon"),
            "url": meta.get("url"),
            "temp_celsius": live_temp,       # Now live!
            "snow_depth_cm": avg_snow,
            "lift_status": formatted_lifts,
            "live_weather": weather_desc,    # Now live!
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        final_output.append(resort_obj)

    # Save to both root and frontend public for fe local fetch().
    output_paths = [
        os.path.join('..', 'resort_data.json'),
        os.path.join('..', 'frontend', 'public', 'resort_data.json'),
    ]
    for output_file in output_paths:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=4, ensure_ascii=False)
        print(f"File saved to: {output_file}")

    print("Exported--")
    conn.close()

if __name__ == "__main__":
    export_json()