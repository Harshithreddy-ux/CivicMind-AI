from backend.agents.base import BaseAgent
from backend.services.aqi_service import AQIAPI

class AQIAgent(BaseAgent):
    def __init__(self):
        self.service = AQIAPI()

    async def process(self, context: dict) -> dict:
        location = context.get("location", "Unknown")
        try:
            data = self.service.get_aqi(location)
            if not data:
                return self.format_error(Exception("AQI data not found."))
            return self.format_success(data, summary=f"Current AQI loaded for {location}.")
        except Exception as e:
            return self.format_error(e)
