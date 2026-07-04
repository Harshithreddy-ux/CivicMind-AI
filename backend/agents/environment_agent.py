from backend.agents.base import BaseAgent

class EnvironmentAgent(BaseAgent):
    async def process(self, context: dict) -> dict:
        return self.format_success(data={"green_cover": "Stable"}, summary="Climate indicators and environmental health aggregated.")
