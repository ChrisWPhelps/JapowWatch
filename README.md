# Japow Watch

This project aggregates live weather and mountain conditions for Japan ski resorts and produces a JSON payload for the frontend app.

## Project structure

| Path | Purpose |
|------|---------|
| **`run_backend.sh`** | Default backend pipeline: crawl → parser tests → export (from repo root), then prints optional frontend start command. |
| **`requirements.txt`** | Python dependencies (install into a virtual environment). |
| **`resort_data.json`** | Generated at repo root after a successful export (gitignored). |
| **`tests/`** | Pytest suite; `test_parsers.py` validates scraper output shape and optional checks on `resort_data.json`. |
| **`frontend/`** | React app (Create React App). Work in progress; see `frontend/README.md` for CRA scripts. |
| **`backend/crawler.py`** | Runs configured resort parsers and writes `backend/data/scraper_results.json`. |
| **`backend/export_to_frontend.py`** | Merges scrape results, SQLite resort metadata, and live weather into `resort_data.json`. |
| **`backend/script.py`** | OpenWeather helper (`get_weather_for_coords`); used by export. Running as `__main__` inserts weather rows into `daily_stats`. |
| **`backend/main.py`** | Full chain: crawler → `script.py` → `batch_update.py` → export (no pytest step). |
| **`backend/batch_update.py`** | Updates `daily_stats` in SQLite from `scraper_results.json` (optional path; not used by `run_backend.sh`). |
| **`backend/init_db.py`** | Creates/seeds `backend/data/japow_watch.db` (see warning below). |
| **`backend/scheduler.py`** | Optional daily runner that invokes `main.py` (not `run_backend.sh`). |
| **`backend/data/`** | SQLite DB and raw scraper JSON (some artifacts may be gitignored). |
| **`backend/parsers/`** | Per-resort scraping logic; shared helpers such as `parsers/snow_contract.py`. |

## How the pipeline works

### Default pipeline (recommended): `run_backend.sh`

Run from the **repo root**. If the script is not executable, use `chmod +x run_backend.sh` once, or run `bash run_backend.sh`.

Steps:

1. **`backend/crawler.py`** — runs the configured resort parsers; writes `backend/data/scraper_results.json`.
2. **`pytest tests/test_parsers.py`** — validates scraper output (schema, numeric snow depths, lifts). Tests run **before** export in this script. The test file may also assert on **`resort_data.json` if it already exists** from a previous run (e.g. weather and coordinates); on a first-time setup that block is skipped until after you have produced at least one export.
3. **`backend/export_to_frontend.py`** — writes **`resort_data.json`** at the repo root and **`frontend/public/resort_data.json`** for local frontend fetches.

### Full backend pipeline: `python backend/main.py`

Run from repo root (or any directory; the script sets backend cwd for subprocesses):

1. `crawler.py`
2. `script.py` (weather API → inserts into `daily_stats`)
3. `batch_update.py` (updates `daily_stats` with snow + lift status from the scrape)
4. `export_to_frontend.py`

**Difference from `run_backend.sh`:** `main.py` does **not** run pytest. **`backend/scheduler.py`** calls `main.py`, not `run_backend.sh`, so scheduled runs skip the test gate.

## Installation (step-by-step)

Do these from the **repository root** unless noted.

### 1) Python

Use **Python 3.11+** (3.14.2 ). The repo is developed with a current 3.x release; avoid versions older than 3.11 unless you verify dependencies yourself.

### 2) Node.js LTS (for npm)

Install from https://nodejs.org/ (if you have a terminal/IDE open close it after the install for PATH refresh)


### 3) Virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
```

### 4) Browser for Selenium

Several parsers use **Selenium with Chrome** (`webdriver.Chrome()`). Install [Google Chrome](https://www.google.com/chrome/) (or a Chromium-compatible browser supported by your Selenium setup). Selenium 4 can resolve the matching ChromeDriver automatically in many environments.

### 5) API key

Create a `.env` file in the repo root (same folder as `README.md`):

```env
OPENWEATHER_API_KEY=your_key_here
```

Sign up at [OpenWeather](https://openweathermap.org/api) for a key. The export path loads this via [python-dotenv](https://github.com/theskumar/python-dotenv).

### 6) Install Python dependencies

With the venv activated:

```bash
pip install -r requirements.txt
```

### 7) Initialize the database

```bash
python backend/init_db.py
```

**Warning:** `init_db.py` **drops and recreates** the `resorts` table and re-seeds it. Do not run it on a database you have customized manually unless you intend to reset resort metadata.

### 8) Make the run script executable (Unix/macOS)

```bash
chmod +x run_backend.sh
```

## Running and interacting with the software

All commands below assume the **repo root** as the current working directory and an **activated virtual environment**.

### End-to-end backend (with tests)

```bash
./run_backend.sh
# or: bash run_backend.sh
```

The script stays backend-only; after a successful export it prints:

```bash
cd frontend && npm start
```

### Output

After a successful run, you get:
- **`resort_data.json`** in the repo root
- **`frontend/public/resort_data.json`** for Create React App static serving

### Other entry points

| Command | What it does |
|---------|----------------|
| `python backend/crawler.py` | Scrape only → `backend/data/scraper_results.json` |
| `python backend/export_to_frontend.py` | Export only (expects existing `scraper_results.json` and DB) |
| `python backend/main.py` | Full chain including DB `daily_stats` updates; no pytest |
| `python backend/scheduler.py` | Daily schedule for `main.py` (keep process running; see env vars in that file) |

### Frontend (optional, WIP)

```bash
cd frontend
npm install
npm start
```

See [`frontend/README.md`](frontend/README.md) (Create React App).

### Tests

```bash
python -m pytest tests/
```

`run_backend.sh` runs only `pytest tests/test_parsers.py` after crawling.

## Daily schedule (optional)

- **Python process:** run `python backend/scheduler.py` under tmux, systemd, or a Windows service. Uses `main.py` (not `run_backend.sh`). Env: `SCHEDULE_TIME` (default `06:30`), `SCHEDULE_RUN_ON_START=1` for an immediate first run.
- **OS scheduler:** use cron or Task Scheduler to run `bash run_backend.sh` (or full path) once per day if you want the **pytest** gate on each run.

## Technical notes

### Data integration

Resort names returned by parsers must match the **`resorts.name`** values seeded by `init_db.py` so export can join coordinates and URLs. Mismatches yield missing lat/lon in `resort_data.json`.

### Furano vs Furapuri (naming)

The live site uses **Furapuri** branding, but the DB seed uses **`Furano Ski Resort`**. The parser is aligned so export resolves coordinates from `init_db.py`.

### Frontend contract

`resort_data.json` uses `lift_status` as an array of `{ "name", "status" }` objects for straightforward UI mapping.

## Tech stack

- Python 3.11+
- SQLite3 (`backend/data/japow_watch.db`)
- JSON for scrape bundle and frontend export
- OpenWeather Current Weather API (via `requests` + `script.py`)
- Selenium and Beautiful Soup for selected resort parsers

## Attribution and third-party resources

| Resource | Use in this project | Link |
|----------|---------------------|------|
| OpenWeather | Current weather API for temperature and conditions | [https://openweathermap.org/api](https://openweathermap.org/api) |
| Selenium | Browser automation for dynamic resort pages | [https://www.selenium.dev/](https://www.selenium.dev/) |
| Beautiful Soup | HTML parsing | [https://www.crummy.com/software/BeautifulSoup/](https://www.crummy.com/software/BeautifulSoup/) |
| Requests | HTTP client | [https://requests.readthedocs.io/](https://requests.readthedocs.io/) |
| python-dotenv | Load `.env` for the API key | [https://github.com/theskumar/python-dotenv](https://github.com/theskumar/python-dotenv) |
| pytest | Test runner | [https://pytest.org/](https://pytest.org/) |
| schedule | Daily scheduling in `scheduler.py` | [https://github.com/dbader/schedule](https://github.com/dbader/schedule) |
| pandas / numpy | Transitive or auxiliary use per `requirements.txt` | [https://pandas.pydata.org/](https://pandas.pydata.org/), [https://numpy.org/](https://numpy.org/) |
| Create React App | Frontend tooling (`frontend/`) | [https://github.com/facebook/create-react-app](https://github.com/facebook/create-react-app) |

**Data sources:** Snow and lift information is scraped from **public resort websites**; site names and URLs are reflected in parser code and the DB seed. Respect each site’s terms of use and robots policy.
