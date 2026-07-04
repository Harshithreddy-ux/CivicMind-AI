from backend.agents.base import BaseAgent
from backend.services.weather_service import WeatherService
import asyncio

class WeatherAgent(BaseAgent):
    def __init__(self):
        self.service = WeatherService()

    async def process(self, context: dict) -> dict:
        location = context.get("location", "Unknown")
        try:
            data = self.service.get_weather(location)
            if not data:
                return self.format_error(Exception("Weather data not found."))
            return self.format_success(data, summary=f"Current weather loaded for {location}.")
        except Exception as e:
            return self.format_error(e)
