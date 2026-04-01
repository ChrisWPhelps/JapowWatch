"""
Run the full backend pipeline (main.py) once per day at a configured local time.

Requires the `schedule` package (see requirements.txt). Keep this process running
with tmux, systemd, or a Windows service; alternatively use cron / Task Scheduler
to invoke run_backend.sh once daily (see README).

Environment:
  SCHEDULE_TIME       Local time HH:MM, default 06:30
  SCHEDULE_RUN_ON_START  If set to 1, run the pipeline once when the process starts
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import schedule

BACKEND_DIR = Path(__file__).resolve().parent
PYTHON = sys.executable
MAIN = BACKEND_DIR / "main.py"


def run_pipeline() -> None:
    print("--- Scheduled pipeline run ---")
    result = subprocess.run([PYTHON, str(MAIN)], cwd=BACKEND_DIR)
    if result.returncode != 0:
        print(f"Pipeline exited with code {result.returncode}")


def main() -> None:
    time_str = os.environ.get("SCHEDULE_TIME", "06:30")
    schedule.every().day.at(time_str).do(run_pipeline)
    print(f"Scheduler: daily pipeline at {time_str} ({BACKEND_DIR})")
    if os.environ.get("SCHEDULE_RUN_ON_START", "").strip() in ("1", "true", "yes"):
        run_pipeline()
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
