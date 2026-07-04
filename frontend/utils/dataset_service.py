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
    rainfall = get_city_rainfall(city)

    base = max(1, population or 1)
    city_scale = min(100.0, max(10.0, base / 10_000_000 * 60.0))

    return {
        "temperature": [24 + city_scale / 16, 25 + city_scale / 14, 27 + city_scale / 12, 29 + city_scale / 10, 31 + city_scale / 9, 30 + city_scale / 11],
        "aqi": [78 + city_scale, 82 + city_scale, 88 + city_scale, 92 + city_scale, 96 + city_scale, 101 + city_scale],
        "humidity": [58 + city_scale / 4, 62 + city_scale / 3, 66 + city_scale / 3, 68 + city_scale / 3, 71 + city_scale / 3, 69 + city_scale / 3],
        "rainfall": [12 + (rainfall or 0) / 8, 14 + (rainfall or 0) / 8, 16 + (rainfall or 0) / 8, 18 + (rainfall or 0) / 8, 17 + (rainfall or 0) / 8, 21 + (rainfall or 0) / 8],
        "population": [max(1, int(base * 0.88)), max(1, int(base * 0.9)), max(1, int(base * 0.92)), max(1, int(base * 0.94)), max(1, int(base * 0.96)), max(1, int(base * 1.0))],
        "crime": [4 + city_scale / 12, 5 + city_scale / 12, 6 + city_scale / 12, 7 + city_scale / 12, 6 + city_scale / 12, 8 + city_scale / 12],
        "flood": [1 + city_scale / 40, 2 + city_scale / 40, 2 + city_scale / 40, 3 + city_scale / 40, 4 + city_scale / 40, 3 + city_scale / 40],
    }
