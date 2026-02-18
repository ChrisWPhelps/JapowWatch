import os
import requests
import pandas as pd
from dotenv import load_dotenv

#API key
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

"""
def get_snow_data(resort_name, lat, lon):
    #temp metric set to celsius
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()  #error check
        data = response.json()

        print(f"--- {resort_name} Status ---")
        print(f"Current Temp: {data['main']['temp']}°C")
        print(f"Conditions: {data['weather'][0]['description']}")

        if data['weather'][0]['main'] == 'Snow':
            print("Snow️")

    except requests.exceptions.RequestException as e:
        print(f"Failed to connect: {e}")
"""

if __name__ == "__main__":

    #Test function get_snow_data("Hakuba Valley Region", 36.6982, 137.8619)
    print("This has compiled-actual functionality removed due to API key req.")