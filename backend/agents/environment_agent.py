from backend.agents.base import BaseAgent
from config.cities import CITIES

class EnvironmentAgent(BaseAgent):
    async def process(self, context: dict) -> dict:
        location = context.get("location", "Unknown")
        city_info = CITIES.get(location)
        region = city_info.get("region", "Central") if city_info else "Central"
        green_cover = "Stable / Forested" if region == "North-East" or region == "South" else "Stable"
        return self.format_success(
            data={"green_cover": green_cover, "region": region}, 
            summary=f"Climate indicators and environmental health aggregated for {region} region."
        )

