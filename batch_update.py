import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'japow_watch.db')

# Mapping scraper names to DB names
NAME_MAP = {
    "Happo-one": "Hakuba Happo-One",
    "Niseko-Village": "Niseko United"
}


def normalize_scraper_data(raw_data):
    """
    Trans crawler list struct -> DB compat format. Converts lift dict into array for indexing on FE.
    """
    try:
        raw_name = raw_data[0].get('resort_name')
        db_name = NAME_MAP.get(raw_name, raw_name) #In case there's name updates-we'll adjust the NAME_MAP[line 9


        depth_dict = raw_data[1]
        depth_values = [int(v) for v in depth_dict.values() if v.isdigit()]
        avg_snow = sum(depth_values) // len(depth_values) if depth_values else 0 #Avg snow depth

        #format Lift Status as an Array of Objects Lift statuses -> array, output should be [{"name": "Grat Quad", "status": "Open"}..
        lift_dict = raw_data[3]
        lift_array = [{"name": k, "status": v} for k, v in lift_dict.items()]

        #store as a JSON string for the DB text column
        lift_json_str = json.dumps(lift_array)

        return db_name, avg_snow, lift_json_str

    except (IndexError, AttributeError, ValueError) as e:
        print(f"FAILURE: Data parsing error: {e}")
        return None


def process_scraper_file(file_name='scraper_results.json'):
    #reads JSON file with scraper results -> updates db.
    file_path = os.path.join(BASE_DIR, file_name)

    if not os.path.exists(file_path):
        print(f"SKIPPING: {file_name} not found. No scraper data to process.")
        return

    try:
        with open(file_path, 'r') as f:
            all_results = json.load(f)
    except json.JSONDecodeError:
        print(f"ERROR: {file_name} is not valid JSON.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    #check if input is single or multiple resortt list
    if isinstance(all_results, list) and len(all_results) > 0:
        if isinstance(all_results[0], list):
            data_to_process = all_results
        else:
            data_to_process = [all_results]
    else:
        return

    for raw_resort_data in data_to_process:
        normalized = normalize_scraper_data(raw_resort_data)
        if not normalized:
            continue

        db_name, snow, lift_status_json = normalized

        cursor.execute("SELECT id FROM resorts WHERE name = ?", (db_name,))
        result = cursor.fetchone()

        if result:
            resort_id = result[0]
            #update scripy.py record
            cursor.execute('''
                UPDATE daily_stats
                SET snow_depth_cm = ?, 
                    lift_status = ?
                WHERE resort_id = ? 
                AND id = (
                    SELECT id FROM daily_stats 
                    WHERE resort_id = ? 
                    ORDER BY timestamp DESC LIMIT 1
                )
            ''', (snow, lift_status_json, resort_id, resort_id))
            print(f"UPDATED: {db_name} | Snow: {snow}cm | Lift Array generated.")
        else:
            print(f"ERROR: Resort '{db_name}' not found in database.")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    process_scraper_file()