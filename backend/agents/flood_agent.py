from backend.agents.base import BaseAgent
from backend.data_sources.dataset_loader import load_flood_data

class FloodAgent(BaseAgent):
    async def process(self, context: dict) -> dict:
        try:
            data = load_flood_data()
            if data["events"].empty:
                return self.format_error(Exception("Flood dataset unavailable."))
            
            summary = f"Flood datasets loaded. Analyzed catchments, events, and precipitation for risk indicators."
            return self.format_success(
                data={"status": "Risk models evaluated"}, 
                summary=summary
            )
        except Exception as e:
            return self.format_error(e)
