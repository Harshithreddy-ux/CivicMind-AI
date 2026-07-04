from backend.agents.base import BaseAgent
from backend.data_sources.dataset_loader import load_crime_data

class CrimeAgent(BaseAgent):
    async def process(self, context: dict) -> dict:
        try:
            df = load_crime_data()
            if df.empty:
                return self.format_error(Exception("Crime dataset unavailable."))
            
            # Very basic statistical extraction for context
            total_crimes = len(df)
            columns = df.columns.tolist()
            
            summary = f"Crime data loaded with {total_crimes} records. Analyzed trends for intent."
            return self.format_success(
                data={"total_records": total_crimes, "features": columns[:5]}, 
                summary=summary
            )
        except Exception as e:
            return self.format_error(e)
