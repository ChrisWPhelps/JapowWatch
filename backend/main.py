import subprocess
import os


def run_step(script_name):
    print(f"{script_name} started")
    result = subprocess.run(['python', script_name], capture_output=True, text=True)

    # Print standard output from the script
    if result.stdout:
        print(result.stdout)

    # Print errors if they occr
    if result.stderr:
        print(f"ERROR in {script_name}:\n{result.stderr}")
    print(f" {script_name} Finished\n")


def main():
    # runs scrapers in the /parsers folder
    run_step('crawler.py')

    #get weather from OpenWeather API-this creates the today's rows in the daily_stats table
    run_step('script.py')

    #udate those rows with snow and lift status from the scraper results.
    run_step('batch_update.py')

    #Generate the final JSON file for the frontend--resort_data.json
    run_step('export_to_json.py')

    print("Pipeline done: resort_data.json is ready for the frontend.")


if __name__ == "__main__":
    main()