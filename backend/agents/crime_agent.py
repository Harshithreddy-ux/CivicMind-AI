from backend.agents.base import BaseAgent
from backend.data_sources.dataset_loader import load_crime_data

# Map state/UT names to representative cities present in crime_dataset_india.csv
STATE_TO_CRIME_CITY = {
    "Andhra Pradesh":           "Visakhapatnam",
    "Bihar":                    "Patna",
    "Gujarat":                  "Ahmedabad",
    "Haryana":                  "Faridabad",
    "Karnataka":                "Bangalore",
    "Madhya Pradesh":           "Bhopal",
    "Maharashtra":              "Mumbai",
    "Punjab":                   "Ludhiana",
    "Rajasthan":                "Jaipur",
    "Tamil Nadu":               "Chennai",
    "Telangana":                "Hyderabad",
    "Uttar Pradesh":            "Lucknow",
    "West Bengal":              "Kolkata",
    "Delhi":                    "Delhi",
    "Jammu and Kashmir":        "Srinagar",
    "Jammu And Kashmir":        "Srinagar",
}

class CrimeAgent(BaseAgent):
    async def process(self, context: dict) -> dict:
        try:
            location = context.get("location", "Unknown")
            df = load_crime_data(location)
            if df.empty:
                return self.format_error(Exception("Crime dataset unavailable."))

            crime_city = STATE_TO_CRIME_CITY.get(location)
            
            if crime_city:
                filtered_df = df[df["City"].str.strip().str.lower() == crime_city.lower()]
            else:
                # Direct check or fallback to state name matches in the City column
                filtered_df = df[df["City"].str.strip().str.lower() == location.lower()]
                
            # If still empty, fall back to a subset of data as fallback
            if filtered_df.empty:
                filtered_df = df.head(100)
                crime_city = "Fallback Regional Core"
            else:
                crime_city = crime_city or location
                
            total_crimes = len(filtered_df)
            
            # Compute top 5 crime categories
            top_crimes = []
            if "Crime Description" in filtered_df.columns:
                top_crimes = filtered_df["Crime Description"].value_counts().head(5).index.tolist()
                
            summary = f"Crime data loaded for {crime_city} with {total_crimes} records. Analyzed regional crime trends."
            return self.format_success(
                data={
                    "total_records": total_crimes, 
                    "city": crime_city,
                    "top_crimes": top_crimes
                }, 
                summary=summary
            )
        except Exception as e:
            return self.format_error(e)

