import requests


class WeatherAPI:

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def get_weather(self, latitude: float, longitude: float):

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "wind_speed_10m"
            ]
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=10
            )

            response.raise_for_status()

            return response.json()

        except Exception as e:

            return {
                "error": str(e)
            }