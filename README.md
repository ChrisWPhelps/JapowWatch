# Japow Watch

Backend data pipeline for Japow Watch. This project aggregates live weather and mountain conditions for Japan ski resorts and provides a JSON payload for the frontend map.

## Tech Stack
* Language: Python 3.14.2
* Database: SQLite3
* APIs: OpenWeather (Current Weather)
* Data Format: JSON

## How the Pipeline Works
1. init_db.py: Sets up SQLite tables and seeds resorts with GPS coordinates.
2. script.py: Hits OpenWeather API for live temperatures and sky conditions.
3. batch_update.py: Merges snow depth and lift status from the crawler into the database.
4. Currently simulating crawler data in scraper_results.json.

## Project Structure
* init_db.py: Run once to create the database (japow_watch.db).
* main.py: Master controller script. Run this to execute the full pipeline at once.
* script.py: Handles API ingestion.
* batch_update.py: Handles crawler data ingestion (reads from scraper_results.json).
* export_to_json.py: Generates resort_data.json for the frontend.

## Setup Instructions
1. API Key: Create a .env file and add: OPENWEATHER_API_KEY=your_key_here.
2. Initialize: Run python init_db.py to build the database.
3. Run Pipeline: Run python main.py.
4. Output: Check resort_data.json for the final data.

---

##CAO 3.18

### Daniel
Please output your crawler data to scraper_results.json. 
**Important:** Ensure your resort names match the database exactly so batch_update.py can find them. If a name is different, it must be added to the NAME_MAP.

### Jhinensky
The resort_data.json is currently generated from dummy data, but the structure is final for crawler integration. 
**Note:** lift_status is an array of objects to allow for easy indexing, lmk if it's not going as expected.