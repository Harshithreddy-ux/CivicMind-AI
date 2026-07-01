import requests

from config.cities import CITIES


class AQIAPI:

    BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

    def get_aqi(self, city):

        city_data = CITIES.get(city)

        if not city_data:
            return None

        latitude = city_data["latitude"]
        longitude = city_data["longitude"]

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "us_aqi"
        }

        try:

            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()

        except Exception:
            return None

        return None