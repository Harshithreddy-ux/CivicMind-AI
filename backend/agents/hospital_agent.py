from backend.agents.base import BaseAgent
from backend.data_sources.dataset_loader import load_hospital_data

class HospitalAgent(BaseAgent):
    async def process(self, context: dict) -> dict:
        try:
            df = load_hospital_data()
            if df.empty:
                return self.format_error(Exception("Hospital dataset unavailable."))
            
            total = len(df)
            summary = f"Hospital directory loaded. Found {total} medical facilities."
            return self.format_success(
                data={"total_hospitals": total}, 
                summary=summary
            )
        except Exception as e:
            return self.format_error(e)
