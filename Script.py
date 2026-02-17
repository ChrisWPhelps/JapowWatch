import os
import requests
import pandas as pd
from dotenv import load_dotenv

# 1. Load the key from the .env file
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_snow_data(resort_name, lat, lon):
    # Use metric units for Celsius
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Checks for errors
        data = response.json()

        print(f"--- {resort_name} Status ---")
        print(f"Current Temp: {data['main']['temp']}°C")
        print(f"Conditions: {data['weather'][0]['description']}")

        if data['weather'][0]['main'] == 'Snow':
            print("Snow️")

    except requests.exceptions.RequestException as e:
        print(f"Failed to connect: {e}")


if __name__ == "__main__":
    # Test with Hakuba coordinates
    get_snow_data("Hakuba", 36.6982, 137.8619)