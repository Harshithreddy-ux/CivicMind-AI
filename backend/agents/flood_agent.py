import pandas as pd
from backend.agents.base import BaseAgent
from backend.data_sources.dataset_loader import load_flood_data
from backend.services.weather_service import WeatherService

# Comprehensive alias map to normalize India state/UT names
_STATE_ALIASES = {
    "jammu & kashmir": "Jammu and Kashmir",
    "jammu and kashmir": "Jammu and Kashmir",
    "j&k": "Jammu and Kashmir",
    "jk": "Jammu and Kashmir",
    "andaman & nicobar islands": "Andaman and Nicobar Islands",
    "andaman and nicobar islands": "Andaman and Nicobar Islands",
    "andaman & nicobar": "Andaman and Nicobar Islands",
    "andaman nicobar": "Andaman and Nicobar Islands",
    "dadra & nagar haveli": "Dadra and Nagar Haveli",
    "dadra and nagar haveli": "Dadra and Nagar Haveli",
    "dadra & nagar haveli and daman & diu": "Dadra and Nagar Haveli",
    "daman & diu": "Daman and Diu",
    "daman and diu": "Daman and Diu",
    "orissa": "Odisha",
    "odisha": "Odisha",
    "pondicherry": "Puducherry",
    "puducherry": "Puducherry",
    "uttaranchal": "Uttarakhand",
    "uttarakhand": "Uttarakhand",
    "ua": "Uttarakhand",
    "north twenty four parganas": "West Bengal",
    "nct of delhi": "Delhi",
    "new delhi": "Delhi",
    "ncr": "Delhi",
    "delhi": "Delhi",
    "ladakh": "Ladakh",
    "lakshadweep": "Lakshadweep",
    "chandigarh": "Chandigarh",
}

def normalize_state_name(state: str) -> str:
    if not state or str(state).strip().lower() in ("nan", "none", ""):
        return ""
    val = str(state).strip().lower()
    if val in _STATE_ALIASES:
        return _STATE_ALIASES[val]
    val = val.replace("&", "and")
    val = " ".join(val.split())
    return val.title()

class FloodAgent(BaseAgent):
    async def process(self, context: dict) -> dict:
        try:
            location = context.get("location", "Unknown")
            state_norm = normalize_state_name(location)
            
            # Load flood datasets
            flood_data = load_flood_data(location)
            events_df = flood_data.get("events", pd.DataFrame())
            catchment_df = flood_data.get("catchment", pd.DataFrame())
            metadata_df = flood_data.get("metadata", pd.DataFrame())

            
            if metadata_df.empty:
                return self.format_error(Exception("Flood metadata unavailable."))
                
            # 1. Filter gauges matching state
            metadata_df["State_Normalized"] = metadata_df["State"].astype(str).apply(normalize_state_name)
            state_gauges = metadata_df[metadata_df["State_Normalized"] == state_norm]
            
            # If no gauges found, fuzzy match first word
            if state_gauges.empty and state_norm:
                first_word = state_norm.split()[0].lower()
                if first_word:
                    state_gauges = metadata_df[metadata_df["State_Normalized"].str.lower().str.contains(first_word, na=False)]
            
            gauge_ids = state_gauges["GaugeID"].tolist()
            num_gauges = len(gauge_ids)
            
            # 2. Get average warning and danger levels
            avg_warning = 50.0
            avg_danger = 70.0
            if not state_gauges.empty:
                avg_warning = float(state_gauges["Warning Level"].mean())
                avg_danger = float(state_gauges["Danger Level"].mean())
                
            # 3. Get average annual precipitation of catchment
            avg_annual_precip = 1200.0
            if not catchment_df.empty and gauge_ids:
                matching_catchments = catchment_df[catchment_df["GaugeID"].isin(gauge_ids)]
                if not matching_catchments.empty:
                    avg_annual_precip = float(matching_catchments["Annual Precipitation"].mean())
                    
            # 4. Get historical maximum peak flood level
            max_historical_peak = 0.0
            if not events_df.empty and gauge_ids:
                # EventID starts with GaugeID, e.g., INDOFLOODS-gauge-1010-1
                # Extract gauge ID prefix
                events_df["GaugeID"] = events_df["EventID"].apply(lambda x: "-".join(str(x).split("-")[:-1]))
                matching_events = events_df[events_df["GaugeID"].isin(gauge_ids)]
                if not matching_events.empty:
                    max_historical_peak = float(matching_events["Peak Flood Level (m)"].max())
            
            # 5. Fetch live weather precipitation
            weather_service = WeatherService()
            weather_resp = await weather_service.get_weather(location)
            live_precip = 0.0
            if weather_resp and "current" in weather_resp:
                live_precip = float(weather_resp["current"].get("precipitation", 0.0))
                
            # 6. Calculate real-time flood risk index
            # Combined score: 60% based on live rain intensity vs 50mm, 40% based on catchment average annual precipitation vs 2500mm
            rain_factor = min(1.0, live_precip / 50.0)
            catchment_factor = min(1.0, avg_annual_precip / 2500.0)
            flood_risk_score = (rain_factor * 60.0) + (catchment_factor * 40.0)
            
            # Map risk score to risk level
            if flood_risk_score >= 80.0 or live_precip > 50.0:
                risk_level = "Critical"
                status = "Emergency alert active. Prepare catchment drainage systems."
            elif flood_risk_score >= 50.0 or live_precip > 20.0:
                risk_level = "High"
                status = "Warning active. Monitor river levels and warning points."
            elif flood_risk_score >= 25.0 or live_precip > 5.0:
                risk_level = "Medium"
                status = "Elevated runoff risk. Normal catchment monitoring."
            else:
                risk_level = "Low"
                status = "No current flood risk observed. Flow levels stable."
                
            summary = f"Flood risk models evaluated for {location}. Calculated dynamic flood risk: {risk_level} ({flood_risk_score:.1f}% index)."
            return self.format_success(
                data={
                    "flood_risk_score": float(f"{flood_risk_score:.2f}"),
                    "risk_level": risk_level,
                    "live_precipitation_mm": live_precip,
                    "avg_annual_precipitation_mm": float(f"{avg_annual_precip:.2f}"),
                    "max_historical_peak_m": float(f"{max_historical_peak:.2f}"),
                    "active_gauges_count": num_gauges,
                    "status_description": status
                },
                summary=summary
            )
        except Exception as e:
            return self.format_error(e)

