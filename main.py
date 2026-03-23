import subprocess
import os


def run_step(script_name):
    print(f"{script_name} STARTED")
    result = subprocess.run(['python', script_name], capture_output=True, text=True)

    # Print standard output from the script
    if result.stdout:
        print(result.stdout)

    # Print errors if they occurred
    if result.stderr:
        print(f"ERROR in {script_name}:\n{result.stderr}")
    print(f" {script_name} Finished\n")


def main():
    # 1. Execute all scrapers in the /scrapers folder
    # This generates a fresh scraper_results.json
    run_step('crawler.py')

    # 2. Get weather from OpenWeather API
    # This creates today's rows in the daily_stats table
    run_step('script.py')

    # 3. Update those rows with snow and lift status from the scraper results
    run_step('batch_update.py')

    # 4. Generate the final JSON file for the frontend
    run_step('export_to_json.py')

    print("PIPELINE COMPLETE: resort_data.json is ready for the frontend.")


if __name__ == "__main__":
    main()