# Japow Watch

This project aggregates live weather and mountain conditions for Japan ski resorts and produces a JSON payload for the frontend app.

## Project Structure
- **/frontend**: React application for data visualization.
- **/backend**: Python scrapers and data processing engine.
- **/backend/data**: Local SQLite database and raw scraper results (ignored by git via `.gitignore`).
- **/backend/parsers**: Directory containing specific scraping logic for each resort.

## How the Pipeline Works

### Default pipeline (recommended): `./run_backend.sh`
This is the quick end-to-end run you can use locally and from a scheduler.
It runs:
1. `backend/crawler.py`
   - Runs the configured resort parsers
   - Writes `backend/data/scraper_results.json`
2. `pytest tests/test_parsers.py`
   - Validates scraper contract and the exported `resort_data.json`
3. `backend/export_to_frontend.py`
   - Writes `resort_data.json` in the repo root

### Full backend pipeline: `python backend/main.py`
This runs the full chain:
1. `crawler.py`
2. `script.py` (weather API ingestion into `daily_stats`)
3. `batch_update.py` (updates `daily_stats` with snow + lift status)
4. `export_to_frontend.py`

## Setup Instructions

### 1) API Key
Create `backend/.env` and add:
`OPENWEATHER_API_KEY=your_key_here`

Note: `./run_backend.sh` changes directory into `backend/`, so the weather loader expects the key in `backend/.env`.

### 2) Install Dependencies
From the repo root:
```bash
pip install -r requirements.txt
```

### 3) Initialize the Database
From the repo root:
```bash
python backend/init_db.py
```

### 4) Run the Pipeline
From the repo root:
```bash
./run_backend.sh
```

### 5) Output
Check `resort_data.json` in the repo root.

## Testing (pytest)
From the repo root:
```bash
python -m pytest tests/
```

`./run_backend.sh` runs only `pytest tests/test_parsers.py` after crawling.

## Daily Schedule (Optional)

The backend can be run once per day (or more often later).

Option 1 (Python process kept alive):
- Run [`backend/scheduler.py`](backend/scheduler.py) and keep the process running (tmux/systemd/Windows service).
- Defaults to 06:30 local time.
- Override with environment variables:
  - `SCHEDULE_TIME` (HH:MM)
  - `SCHEDULE_RUN_ON_START=1` to run immediately on startup

Option 2 (OS scheduler):
- Use cron / Windows Task Scheduler to run `./run_backend.sh` once daily.

## Technical Notes

### Data Integration
Ensure resort names in the scraper scripts match the database exactly so the export script can find them. If a name is different, the export script won't find coordinates and may return `null` fields.

### Furano vs Furapuri (naming)
The live site uses **Furapuri** branding, but the DB seed uses **`Furano Ski Resort`**. The parser is aligned so export picks up coordinates from `init_db.py`.

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
