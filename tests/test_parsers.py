import pytest
import json
import os

# Path to your raw results for quick validation
RESULTS_PATH = os.path.join('backend', 'data', 'scraper_results.json')


def test_scraper_output_exists():
    """Check if the crawler actually produced a file."""
    assert os.path.exists(RESULTS_PATH), "scraper_results.json is missing!"


def test_data_schema():
    """Verify the structure of the scraped data matches the frontend needs."""
    with open(RESULTS_PATH, 'r') as f:
        data = json.load(f)

    for resort in data:
        # Check top-level structure (List of 5 items based on your current output)
        assert len(resort) >= 4, f"Resort entry is malformed: {resort[0]}"

        # Check naming
        assert 'resort_name' in resort[0]

        # Check snow depth is numeric
        snow_data = resort[1]
        for area, depth in snow_data.items():
            assert str(depth).isdigit(), f"Non-numeric snow depth found in {resort[0]['resort_name']}"

        # Check lift status isn't empty
        lift_data = resort[3]
        assert len(lift_data) > 0, f"No lifts found for {resort[0]['resort_name']}"


def test_final_export_validity():
    """Verify the final resort_data.json has live weather and valid coordinates."""
    export_path = 'resort_data.json'

    # Skip if the file hasn't been generated yet
    if not os.path.exists(export_path):
        return

    with open(export_path, 'r') as f:
        data = json.load(f)

    for resort in data:
        # Check that weather isn't the default 'unknown'
        assert resort['live_weather'] != "unknown", f"Weather failed for {resort['name']}"

        # Check that coordinates are actually present
        assert resort['lat'] is not None, f"Missing latitude for {resort['name']}"
        assert resort['lon'] is not None, f"Missing longitude for {resort['name']}"

        # Check that temperature is a float or int (not a string)
        assert isinstance(resort['temp_celsius'], (int, float))