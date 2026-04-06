# Japow Watch

Japow Watch aggregates live conditions for selected Japan ski resorts and exports a frontend-ready JSON payload.

## Project structure

| Path | Purpose |
|------|---------|
| `run_backend.sh` | Recommended backend pipeline: crawl -> parser tests -> export. |
| `requirements.txt` | Python dependencies for backend scripts and tests. |
| `backend/` | Scrapers, DB setup, export logic, and optional helper scripts. |
| `backend/crawler.py` | Runs configured resort parsers and writes `backend/data/scraper_results.json`. |
| `backend/export_to_frontend.py` | Merges scrape output + DB metadata + live weather, then writes export JSON files. |
| `backend/script.py` | OpenWeather helper (`get_weather_for_coords`); CLI mode inserts weather into `daily_stats`. |
| `backend/main.py` | Alternate full chain runner: `crawler.py` -> `script.py` -> `batch_update.py` -> `export_to_frontend.py` (no pytest). |
| `backend/batch_update.py` | Attempts to update latest `daily_stats` rows with snow/lift data from a scrape JSON file (defaults to `backend/data/scraper_results.json`). |
| `backend/init_db.py` | Creates/seeds `backend/data/japow_watch.db`. Drops and recreates `resorts`. |
| `backend/parsers/` | Per-resort parsers and shared parser contract helpers. |
| `tests/` | Pytest suite (`test_parsers.py`, `test_snow_contract.py`). |
| `frontend/` | Create React App frontend (`npm start` from this directory). |

### Frontend (`frontend/`)

| Path | Purpose |
|------|---------|
| `public/resort_data.json` | Static JSON consumed by the app at `/resort_data.json` (written by export). |
| `public/` | Other static assets (e.g. `index.html`, favicon). |
| `src/index.js` | React entry (renders `App`). |
| `src/index.css` | Global styles. |
| `src/App.js` | Main UI: loads resort data, list + map layout. |
| `src/App.css` | App and layout styles. |
| `src/ResortCard.js` | Single resort summary card. |
| `src/LeafletMap.js` | Map view (Leaflet / react-leaflet). |
| `src/utils.js` | Shared helpers. |
| `src/setupTests.js`, `src/App.test.js` | CRA test wiring. |
| `src/reportWebVitals.js` | CRA performance reporting. |

## Requirements

### Backend runtime

- Python 3.14.2+
- `pip install -r requirements.txt`
- Google Chrome (for Selenium-based parsers)
- OpenWeather API key in `.env` at repo root:

```env
OPENWEATHER_API_KEY=your_key_here
```

### Frontend runtime

- Node.js LTS (includes npm)
- Run frontend commands from `frontend/`

## Setup (fresh clone)

All steps assume Node.js LTS and Python 3.14.2+ are installed.

From repo root:

```bash
git clone https://github.com/ChrisWPhelps/JapowWatch.git
cd JapowWatch
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
# source .venv/bin/activate      # macOS/Linux
python -m pip install --upgrade pip
pip install -r requirements.txt
python backend/init_db.py
```

`init_db.py` warning: it drops/recreates the `resorts` table and reseeds resort metadata.

Get your API key from: [OpenWeather API](https://openweathermap.org/api)

Create a `.env` file in the repo root:

```env
OPENWEATHER_API_KEY=your_key_here
```

## Running

All backend commands assume repo root, activated virtual environment, a `.env` file in the root with an active API key, and Node.js installed.

### Recommended pipeline (with parser tests)

```bash
bash run_backend.sh
```

This runs:

1. `python backend/crawler.py`
2. `pytest tests/test_parsers.py`
3. `python backend/export_to_frontend.py`

On success, the script prints the optional frontend next step:

```bash
cd frontend && npm install && npm start
```

### Alternate pipeline (no pytest gate)

```bash
python backend/main.py
```

This runs:

1. `crawler.py`
2. `script.py`
3. `batch_update.py`
4. `export_to_frontend.py`

## Outputs

After a successful export:

- `backend/data/scraper_results.json` (crawler output)
- `resort_data.json` (root export payload)
- `frontend/public/resort_data.json` (frontend static fetch path)

## Frontend

From `frontend/`:

```bash
npm install
npm start
```

The app opens in your browser on localhost.

The app fetches data from `/resort_data.json`, served from `frontend/public/resort_data.json`.

## Tests

If you want to run all tests:

```bash
python -m pytest tests/
```

`run_backend.sh` runs `tests/test_parsers.py` only.

## Automation

Use your OS scheduler (cron or Task Scheduler) to run `bash run_backend.sh` daily if you want the pytest gate on scheduled runs.

## Known limitations

- If weather lookup fails or coordinates are missing, export falls back to `temp_celsius = 0.0` and `live_weather = "unknown"` for that resort.

## Tech stack

- Python (requests, selenium, beautifulsoup4, pytest, python-dotenv)
- SQLite (`backend/data/japow_watch.db`)
- React + Create React App (`frontend/`)
- Leaflet (`leaflet`, `react-leaflet`)

## Third-party resources

- [OpenWeather API](https://openweathermap.org/api)
- [Selenium](https://www.selenium.dev/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- [Requests](https://requests.readthedocs.io/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [pytest](https://pytest.org/)
- [Create React App](https://github.com/facebook/create-react-app)

Data is scraped from public resort websites. Respect each site’s terms and robots policy.
