from backend.agents.base import BaseAgent
from config.cities import CITIES

class TrafficAgent(BaseAgent):
    async def process(self, context: dict) -> dict:
        location = context.get("location", "Unknown")
        city_info = CITIES.get(location)
        pop = city_info.get("population", 1000000) if city_info else 1000000
        congestion = "Heavy" if pop > 40000000 else ("Moderate" if pop > 10000000 else "Light")
        return self.format_success(
            data={"congestion": congestion, "scale": pop}, 
            summary=f"Traffic routing evaluated. Congestion pattern: {congestion} for {location}."
        )

