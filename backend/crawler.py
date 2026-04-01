import json
import os
from datetime import datetime

# Import individual resort parsers from the 'parsers' directory
from parsers import (
    aomori_spring,
    furano_ski_resort,
    geto_kogen_resort,
    hakuba_cortina,
    hakuba,
    hoshino_resorts_tomamu,
    ishiuchi,
    kandatsu_kogen,
    kiroro_snow_world,
    madarao_mountain_resort,
    myoko_akakura_onsen,
    niseko_united,
    rusutsu,
    sapporo_teine,
    sapporo_kokusai,
)
from parsers.snow_contract import normalize_scraper_result


def run_crawler():
    start_time = datetime.now()
    print(f"--- STARTING CRAWL AT {start_time.strftime('%H:%M:%S')} ---")

    # This list will hold the 'Final Return' from every resort parser
    all_resort_data = []

    # task list - needs to be updated as crawlers are finished.
    tasks = [
        ("Aomori Spring", aomori_spring.get_data),
        ("Furano Ski Resort", furano_ski_resort.get_data),
        ("Geto Kogen Resort", geto_kogen_resort.get_data),
        ("Hakuba Cortina", hakuba_cortina.get_data),
        ("Hakuba", hakuba.get_data),
        ("Hoshino Resorts TOMAMU", hoshino_resorts_tomamu.get_data),
        ("Ishiuchi Maruyama", ishiuchi.get_data),
        ("Kandatsu Kogen", kandatsu_kogen.get_data),
        ("Kiroro Snow World", kiroro_snow_world.get_data),
        ("Madarao Mountain Resort", madarao_mountain_resort.get_data),
        ("Myoko Akakura Onsen", myoko_akakura_onsen.get_data),
        ("Niseko United", niseko_united.get_data),
        ("Rusutsu", rusutsu.get_data),
        ("Sapporo Teine", sapporo_teine.get_data),
        ("Sapporo Kokusai", sapporo_kokusai.get_data),
    ]

    success_count = 0
    total_tasks = len(tasks)

    for name, get_data_func in tasks:
        try:
            print(f"Scraping {name}...")
            data = get_data_func()
            # Contract safety: normalize depth/new-snow values so export/tests
            # never see dash placeholders like "-" or "—".
            all_resort_data.append(normalize_scraper_result(data))
            success_count += 1
            print(f"  [SUCCESS] {name} updated.")
        except Exception as e:
            print(f"  [ERROR] Scraping {name}: {e}")

    base_dir = os.path.dirname(__file__)
    output_file = os.path.join(base_dir, 'data', 'scraper_results.json')

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_resort_data, f, indent=4, ensure_ascii=False)
        print(f"\nMaster file saved to {output_file}")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Failed to save JSON: {e}")

    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "=" * 40)
    print(f"CRAWL COMPLETE")
    print(f"Status: {success_count}/{total_tasks} resorts successfully scraped.")
    print(f"Duration: {duration.total_seconds():.2f} seconds")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    run_crawler()