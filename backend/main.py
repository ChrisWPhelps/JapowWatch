import subprocess
import os
import sys


def run_step(script_name):
    print(f"{script_name} started")
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    result = subprocess.run(
        [sys.executable, script_name],
        cwd=backend_dir,
        capture_output=True,
        text=True,
    )

    # Print standard output from the script
    if result.stdout:
        print(result.stdout)

    # Print errors if they occr
    if result.stderr:
        print(f"ERROR in {script_name}:\n{result.stderr}")
    print(f" {script_name} Finished\n")


def main():
    run_step('crawler.py')

    run_step('script.py')

    run_step('batch_update.py')

    run_step('export_to_frontend.py')

    print("Pipeline done: resort_data.json is ready for the frontend.")


if __name__ == "__main__":
    main()