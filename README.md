# Japow Watch

This project aggregates live weather and mountain conditions for Japan ski resorts and provides a JSON payload to be used by the frontend app.

## Project Structure
- **/frontend**: React application for data visualization.
- **/backend**: Python scrapers and data processing engine.
- **/backend/data**: Local SQLite database and raw scraper results (Git ignored).
- **/backend/parsers**: Directory containing specific scraping logic for each mountain.

## How the Pipeline Works
1. **init_db.py**: Sets up SQLite tables and seeds 40 resorts with GPS coordinates.
2. **crawler.py**: The master scraper that triggers the 9 verified resort scripts and saves raw data to scraper_results.json.
3. **script.py**: Handles OpenWeather API ingestion for live temperatures and sky conditions.
4. **export_to_frontend.py**: Transforms raw scraper data and live weather into the final JSON format.

## Setup Instructions
1. **API Key**: Create a .env file in the /backend directory and add: `OPENWEATHER_API_KEY=your_key_here`.
2. **Install Dependencies**: Run `pip install -r requirements.txt` from the root directory.
3. **Initialize**: From the root directory, run `python init_db.py` to build the database.
4. **Run Pipeline**: From the root directory, execute `./run_backend.sh`.
5. **Output**: Check `resort_data.json` in the root directory for the final data.

---

## Technical Notes

### Data Integration
Ensure resort names in the scraper scripts match the database exactly so the export script can find them. If a name is different, the script will return null coordinates.

### Frontend Contract
The `resort_data.json` structure is final. The `lift_status` field is an array of objects to allow for easy mapping in the frontend application.

## Tech Stack
- Language: Python 3.14.2
- Database: SQLite3
- APIs: OpenWeather (Current Weather)
- Data Format: JSON



## Notes CAO 3.27
-J Frontend: Make sure payload works/finalize front end design
-D Backend: Add the scrapers you've been working on + keep pushing towards the goal
-C Backend: Scrapers / Update DB seeding
