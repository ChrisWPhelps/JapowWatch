import subprocess
import os

def run_step(script_name):
    print(f"Running {script_name}")
    result = subprocess.run(['python3', script_name], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"ERROR in {script_name}: {result.stderr}")


def main():
    #gets weather from OW API and creates todays rows in db.
    run_step('script.py')

    #update rows with snow/lift status
    ##We're using a sample data from one resort from the scraper, when we get to it/in production, the scraper would trigger this
    run_step('batch_update.py')

    #Generates the JSON file for FE.
    run_step('export_to_json.py')

    print("pipeline finished: resort_data.json for export to FE")


if __name__ == "__main__":
    main()