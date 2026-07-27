from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import math

from config.cities import CITIES
from backend.services.enricher import enrich_hospital_coordinates, get_enriched_flood_gauges

ROOT = Path(__file__).resolve().parents[1]
DATASETS_ROOT = ROOT.parent / "datasets"

# ── Comprehensive alias map: normalizes any variant to the CSV-compatible form ──
_STATE_ALIASES: dict = {
    # & / and variants
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
    # Old/alternate names
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
    # Union Territories
    "ladakh": "Ladakh",
    "lakshadweep": "Lakshadweep",
    "chandigarh": "Chandigarh",
}

def normalize_state_name(state: str) -> str:
    """Normalize any India state/UT name variant to the canonical form used in CSVs."""
    if not state or str(state).strip().lower() in ("nan", "none", ""):
        return ""
    val = str(state).strip().lower()
    # Check alias map first (handles & vs and, old names, etc.)
    if val in _STATE_ALIASES:
        return _STATE_ALIASES[val]
    # Generic &→and replacement then title-case
    val = val.replace("&", "and")
    val = " ".join(val.split())
    return val.title()


@lru_cache(maxsize=1)
def load_all_datasets() -> Dict[str, pd.DataFrame]:
    datasets: Dict[str, pd.DataFrame] = {}
    if not DATASETS_ROOT.exists():
        return datasets

    # Load all CSV files completely (removed the truncation of hospital directory to prevent missing states)
    for csv_path in sorted(DATASETS_ROOT.glob("*.csv")):
        try:
            key = csv_path.stem.lower()
            datasets[key] = pd.read_csv(csv_path, low_memory=False)
        except Exception:
            continue

    return datasets

def get_dataset(name: str) -> Optional[pd.DataFrame]:
    return load_all_datasets().get(name.lower())

def is_coordinates_sane(lat: float, lon: float, base_lat: float, base_lon: float) -> bool:
    """Verifies coordinates are within India boundaries and within a reasonable distance from state center."""
    # 1. Broad India boundary check
    if not (6.0 <= lat <= 38.0 and 68.0 <= lon <= 98.0):
        return False
        
    # 2. Distance check from capital (should not be farther than 3.5 degrees to avoid cross-country coordinate mapping errors)
    dist = math.sqrt((lat - base_lat)**2 + (lon - base_lon)**2)
    if dist > 3.5:
        return False
        
    return True

def get_city_facilities(city: str, dataset_name: str) -> List[Dict[str, Any]]:
    # Match query using normalized name matching
    query_norm = normalize_state_name(city)
    
    if dataset_name.lower() in ("hospitals", "hospital_directory"):
        frame = get_dataset("hospital_directory")
        if frame is not None:
            # Normalize CSV state column using the same comprehensive alias map
            frame_states = frame["State"].astype(str).apply(normalize_state_name)
            matches = frame[frame_states == query_norm]
            
            # Fuzzy partial fallback if exact match fails
            if matches.empty:
                # Use the first word of the query for partial matching
                first_word = query_norm.split()[0].lower() if query_norm else ""
                if first_word:
                    matches = frame[frame_states.str.lower().str.contains(first_word, na=False)]
                    
            city_info = CITIES.get(city, {})
            base_lat = city_info.get("latitude", 20.5937)
            base_lon = city_info.get("longitude", 78.9629)
            
            city_matches = []
            
            # If no hospitals found (e.g. Delhi, Ladakh not in CSV), generate
            # synthetic dispersion markers around the capital so the map is not empty
            if matches.empty:
                import random as _rnd
                rng = _rnd.Random(hash(city + "_hosp"))
                num_fallback = 15 if city == "Ladakh" else 25
                for i in range(num_fallback):
                    lat = base_lat + rng.uniform(-0.12, 0.12)
                    lon = base_lon + rng.uniform(-0.12, 0.12)
                    city_matches.append({
                        "Hospital": f"{city} Medical Facility #{i+1}",
                        "Latitude": lat,
                        "Longitude": lon,
                        "City": city,
                        "State": city,
                        "District": "",
                        "Category": "General",
                        "Care_Type": "Multi-Specialty",
                        "source": "Estimated (Not in NHP registry)",
                    })
                return city_matches
            
            for _, row in matches.iterrows():
                coords_str = str(row.get("Location_Coordinates", ""))
                lat, lon = None, None
                source = "Local Dataset"
                
                if coords_str and "," in coords_str:
                    try:
                        parts = coords_str.split(",")
                        lat = float(parts[0].strip())
                        lon = float(parts[1].strip())
                    except Exception:
                        pass
                
                if lat is None or lon is None or not is_coordinates_sane(lat, lon, base_lat, base_lon):
                    hosp_name = str(row.get("Hospital_Name", "Unknown Hospital"))
                    dist = str(row.get("District", ""))
                    lat, lon, source = enrich_hospital_coordinates(hosp_name, dist, city)
                
                city_matches.append({
                    "Hospital": str(row.get("Hospital_Name", "Unknown Hospital")),
                    "Latitude": lat,
                    "Longitude": lon,
                    "City": city,
                    "State": str(row.get("State", "")),
                    "District": str(row.get("District", "")),
                    "Category": str(row.get("Hospital_Category", "Private")),
                    "Care_Type": str(row.get("Hospital_Care_Type", "General")),
                    "source": source
                })
            return city_matches

    # Fallback/General logic for other datasets
    frame = get_dataset(dataset_name)
    if frame is None:
        return []

    if "City" not in frame.columns:
        return []

    city_matches = []
    for _, row in frame.iterrows():
        if normalize_state_name(str(row["City"])) == query_norm:
            city_matches.append({key: str(value) for key, value in row.items()})

    return city_matches

def get_city_population(city: str) -> Optional[int]:
    if city in CITIES:
        return CITIES[city].get("population")
    return 1000000

def get_city_rainfall(city: str) -> Optional[float]:
    frame = get_dataset("sub_division_imd_2017")
    if frame is not None:
        subdivs = frame["SUBDIVISION"].astype(str).str.strip().str.lower()
        query = city.strip().lower()
        
        matches = frame[subdivs.str.contains(query) | subdivs.apply(lambda x: query in x)]
        if not matches.empty:
            latest_row = matches.sort_values(by="YEAR").iloc[-1]
            try:
                val = latest_row.get("ANNUAL")
                if val is not None and not pd.isna(val):
                    return float(val)
            except Exception:
                pass

    # Fallback to regional default averages if dataset is missing/empty
    if city in CITIES:
        region = CITIES[city].get("region", "")
        if region == "South":
            return 1150.0
        elif region == "North-East":
            return 2200.0
        elif region == "East":
            return 1450.0
        elif region == "West":
            return 950.0
        elif region == "North":
            return 800.0
    return 1000.0

def get_city_trend_series(city: str) -> Dict[str, List[float]]:
    population = get_city_population(city)
    base = max(1, population or 1)
    city_scale = min(100.0, max(10.0, base / 10_000_000 * 60.0))

    # Representative crime city mapping to avoid circular imports
    state_to_crime = {
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
    }

    # 1. Real Rainfall historical trends
    rain_trend = []
    rain_frame = get_dataset("sub_division_imd_2017")
    if rain_frame is not None:
        subdivs = rain_frame["SUBDIVISION"].astype(str).str.strip().str.lower()
        query = city.strip().lower()
        matches = rain_frame[subdivs.str.contains(query) | subdivs.apply(lambda x: query in x)]
        if not matches.empty:
            sorted_matches = matches.sort_values(by="YEAR")
            rain_trend = [float(v) for v in sorted_matches["ANNUAL"].values[-6:]]

    if len(rain_trend) < 6:
        avg_rain = get_city_rainfall(city) or 1000.0
        rain_trend = [avg_rain * r for r in [0.9, 0.95, 1.05, 1.0, 0.88, 1.1]]

    # 2. Real Crime trends over time (by year)
    crime_trend = []
    crime_frame = get_dataset("crime_dataset_india")
    if crime_frame is not None and not crime_frame.empty:
        crime_city = state_to_crime.get(normalize_state_name(city))
        if crime_city:
            filtered_crime = crime_frame[crime_frame["City"].str.strip().str.lower() == crime_city.lower()].copy()
        else:
            filtered_crime = crime_frame[crime_frame["City"].str.strip().str.lower() == city.lower()].copy()
            
        if filtered_crime.empty:
            filtered_crime = crime_frame.head(200).copy()
            
        # Extract year from 'Date Reported'
        filtered_crime["Year"] = filtered_crime["Date Reported"].apply(lambda x: str(x)[6:10] if len(str(x)) >= 10 else None)
        crime_by_year = filtered_crime.groupby("Year").size().sort_index()
        crime_trend = [int(v) for v in crime_by_year.values[-6:]]

    if len(crime_trend) < 6:
        crime_trend = [int(150 + city_scale * r) for r in [1.0, 1.1, 1.3, 1.25, 1.4, 1.5]]

    # 3. Real Flood events trends over time
    flood_trend = []
    flood_data = get_dataset("floodevents_indofloods")
    metadata_frame = get_dataset("metadata_indofloods")
    if flood_data is not None and not flood_data.empty and metadata_frame is not None:
        query_norm = normalize_state_name(city)
        metadata_frame["State_Normalized"] = metadata_frame["State"].astype(str).apply(normalize_state_name)
        state_gauges = metadata_frame[metadata_frame["State_Normalized"] == query_norm]
        if not state_gauges.empty:
            gauge_ids = state_gauges["GaugeID"].tolist()
            flood_copy = flood_data.copy()
            flood_copy["GaugeID"] = flood_copy["EventID"].apply(lambda x: "-".join(str(x).split("-")[:-1]))
            state_events = flood_copy[flood_copy["GaugeID"].isin(gauge_ids)].copy()
            if not state_events.empty:
                state_events["Year"] = state_events["Start Date"].apply(lambda x: str(x)[:4] if len(str(x)) >= 4 else None)
                flood_by_year = state_events.groupby("Year").size().sort_index()
                flood_trend = [int(v) for v in flood_by_year.values[-6:]]

    if len(flood_trend) < 6:
        flood_trend = [int(2 + city_scale / 30 + r) for r in [0, 1, 1, 2, 1, 3]]

    return {
        "temperature": [24 + city_scale / 16, 25 + city_scale / 14, 27 + city_scale / 12, 29 + city_scale / 10, 31 + city_scale / 9, 30 + city_scale / 11],
        "aqi": [78 + city_scale, 82 + city_scale, 88 + city_scale, 92 + city_scale, 96 + city_scale, 101 + city_scale],
        "humidity": [58 + city_scale / 4, 62 + city_scale / 3, 66 + city_scale / 3, 68 + city_scale / 3, 71 + city_scale / 3, 69 + city_scale / 3],
        "rainfall": rain_trend,
        "population": [max(1, int(base * r)) for r in [0.88, 0.90, 0.92, 0.94, 0.96, 1.0]],
        "crime": crime_trend,
        "flood": flood_trend,
    }
