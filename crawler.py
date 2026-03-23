import json
import os
from datetime import datetime

# Import your individual resort parsers
# These would be your Rusutsu Resort.py and Hakuba Happo-One.py files
# moved into a 'parsers' folder.
from parsers import rusutsu, hakuba


def run_crawler():
    print(f"Starting crawl at {datetime.now().strftime('%H:%M:%S')}")

    # This list will hold the 'Final Return' from every resort
    all_resort_data = []

    # 1. List of parser functions to trigger
    # Each of these returns the [name_dict, snow_dict, snowfall_dict, lift_dict, time_dict] structure
    tasks = [
        ("Rusutsu", rusutsu.get_data),
        ("Hakuba", hakuba.get_data)
    ]

    for name, get_data_func in tasks:
        try:
            print(f"Scraping {name}...")
            data = get_data_func()
            all_resort_data.append(data)
        except Exception as e:
            print(f"Error scraping {name}: {e}")

    # 2. Save the master list to the file the backend expects
    output_file = 'scraper_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_resort_data, f, indent=4, ensure_ascii=False)

    print(f"Crawl complete. Data saved to {output_file}")


if __name__ == "__main__":
    run_crawler()