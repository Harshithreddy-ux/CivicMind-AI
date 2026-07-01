from backend.data_sources.weather_api import WeatherAPI
from config.cities import CITIES


class WeatherService:

    def __init__(self):
        self.weather_api = WeatherAPI()

    def get_weather(self, city: str):

        if city not in CITIES:
            return None

        latitude = CITIES[city]["latitude"]
        longitude = CITIES[city]["longitude"]

        return self.weather_api.get_weather(
            latitude,
            longitude
        )