import os
import json
import time
import requests
import random
from typing import Tuple, Optional, List, Dict, Any
from geopy.geocoders import Nominatim
from config.cities import CITIES

CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "geocoding_cache.json")

# State ISO codes for Overpass API
STATE_ISO_MAP = {
    "Andhra Pradesh": "AP", "Arunachal Pradesh": "AR", "Assam": "AS", "Bihar": "BR",
    "Chhattisgarh": "CG", "Goa": "GA", "Gujarat": "GJ", "Haryana": "HR",
    "Himachal Pradesh": "HP", "Jharkhand": "JH", "Karnataka": "KA", "Kerala": "KL",
    "Madhya Pradesh": "MP", "Maharashtra": "MH", "Manipur": "MN", "Meghalaya": "ML",
    "Mizoram": "MZ", "Nagaland": "NL", "Odisha": "OD", "Punjab": "PB",
    "Rajasthan": "RJ", "Sikkim": "SK", "Tamil Nadu": "TN", "Telangana": "TG",
    "Tripura": "TR", "Uttar Pradesh": "UP", "Uttarakhand": "UK", "West Bengal": "WB",
    "Delhi": "DL", "Puducherry": "PY", "Chandigarh": "CH", "Ladakh": "LA",
    "Lakshadweep": "LD", "Andaman and Nicobar Islands": "AN", "Andaman & Nicobar Islands": "AN",
    "Daman and Diu": "DD", "Daman & Diu": "DD", "Dadra and Nagar Haveli": "DN", "Dadra & Nagar Haveli": "DN",
    "Jammu and Kashmir": "JK", "Jammu & Kashmir": "JK"
}

# Keep track of Nominatim queries in this execution to prevent blocking the user
_NOMINATIM_QUERY_COUNT = 0
MAX_NOMINATIM_QUERIES_PER_RUN = 5

def load_cache() -> Dict[str, Any]:
    if not os.path.exists(CACHE_FILE):
        return {"hospitals": {}, "flood_gauges": {}}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"hospitals": {}, "flood_gauges": {}}

def save_cache(cache: Dict[str, Any]):
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"Error saving geocoding cache: {e}")

_geocoder = Nominatim(user_agent="civicmind_ai_decision_intelligence_v2")

def normalize_string(val: str) -> str:
    if not val or not isinstance(val, str):
        return ""
    return val.strip().lower()

def geocode_location(query_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Safe wrapper for Nominatim geocoding with a rate limit delay and limit cap."""
    global _NOMINATIM_QUERY_COUNT
    if _NOMINATIM_QUERY_COUNT >= MAX_NOMINATIM_QUERIES_PER_RUN:
        # Cap reached, force fallback path to keep response sub-second
        return None, None
        
    try:
        _NOMINATIM_QUERY_COUNT += 1
        time.sleep(1.0)  # Rate limiting compliance
        location = _geocoder.geocode(query_str, timeout=8)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Nominatim lookup error for '{query_str}': {e}")
    return None, None

def enrich_hospital_coordinates(hospital_name: str, district: str, state: str) -> Tuple[float, float, str]:
    """
    Enriches hospital coordinates. 
    1. Checks local cache first.
    2. Queries Nominatim (limited to max 5 new queries per run).
    3. Falls back to dispersing coordinates within the state capital's bounds.
    """
    cache = load_cache()
    hosp_key = f"{normalize_string(hospital_name)}|{normalize_string(district)}|{normalize_string(state)}"
    
    # 1. Check cache
    if hosp_key in cache.get("hospitals", {}):
        cached = cache["hospitals"][hosp_key]
        return cached["lat"], cached["lon"], cached["source"]
        
    # 2. Try Nominatim (only if under the query limit cap)
    search_queries = [
        f"{hospital_name}, {district}, {state}, India",
        f"{hospital_name}, {state}, India",
        f"{district} Hospital, {state}, India"
    ]
    
    for query in search_queries:
        lat, lon = geocode_location(query)
        if lat and lon:
            if 6.0 <= lat <= 38.0 and 68.0 <= lon <= 98.0:
                # Save to cache
                cache.setdefault("hospitals", {})[hosp_key] = {
                    "lat": lat,
                    "lon": lon,
                    "source": "OpenStreetMap / Nominatim"
                }
                save_cache(cache)
                return lat, lon, "OpenStreetMap / Nominatim"
                
    # 3. Fallback to state capital coordinates dispersion
    base_lat, base_lon = 20.5937, 78.9629  # India center
    matched_city = None
    for name, info in CITIES.items():
        if normalize_string(name) == normalize_string(state):
            matched_city = info
            break
            
    if matched_city:
        base_lat = matched_city.get("latitude", base_lat)
        base_lon = matched_city.get("longitude", base_lon)
        
    # Distribute within state boundaries safely
    lat = base_lat + random.uniform(-0.06, 0.06)
    lon = base_lon + random.uniform(-0.06, 0.06)
    
    return lat, lon, "Fallback State Dispersion"

def fetch_overpass_waterways(state: str) -> List[Dict[str, Any]]:
    """Queries the Overpass API for water features (gauges/dams/weirs/rivers) in a state."""
    iso_code = STATE_ISO_MAP.get(state)
    if not iso_code:
        return []
        
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:15];
    area["ISO3166-2"="IN-{iso_code}"]->.searchArea;
    (
      node["waterway"="gauge"](area.searchArea);
      node["waterway"="dam"](area.searchArea);
      node["waterway"="weir"](area.searchArea);
    );
    out body 25;
    """
    try:
        resp = requests.post(overpass_url, data={"data": query}, timeout=15)
        if resp.status_code == 200:
            elements = resp.json().get("elements", [])
            gauges = []
            for el in elements:
                if "lat" in el and "lon" in el:
                    name = el.get("tags", {}).get("name", f"OSM Water Node {el['id']}")
                    gauges.append({
                        "GaugeID": f"OSM-{el['id']}",
                        "Station": name,
                        "Latitude": el["lat"],
                        "Longitude": el["lon"],
                        "State": state,
                        "Warning Level": 100.0,
                        "Danger Level": 120.0,
                        "Reliability": "OSM Enriched",
                        "source": "OpenStreetMap / Overpass"
                    })
            return gauges
    except Exception as e:
        print(f"Overpass query failed for state '{state}': {e}")
    return []

def get_enriched_flood_gauges(state: str) -> List[Dict[str, Any]]:
    """Loads state flood gauges from local cache, queries Overpass if missing, or falls back."""
    cache = load_cache()
    state_key = normalize_string(state)
    
    # 1. Check cache
    if state_key in cache.get("flood_gauges", {}):
        return cache["flood_gauges"][state_key]
        
    # 2. Try Overpass API
    gauges = fetch_overpass_waterways(state)
    if gauges:
        cache.setdefault("flood_gauges", {})[state_key] = gauges
        save_cache(cache)
        return gauges
        
    # 3. Fallback: distribute a couple of mock gauges around the state capital to ensure layer renders
    base_lat, base_lon = 20.5937, 78.9629
    matched_city = None
    for name, info in CITIES.items():
        if normalize_string(name) == state_key:
            matched_city = info
            break
            
    if matched_city:
        base_lat = matched_city.get("latitude", base_lat)
        base_lon = matched_city.get("longitude", base_lon)
        
    fallback_gauges = [
        {
            "GaugeID": f"FALLBACK-{state_key}-1",
            "Station": f"{state} Water Level Sensor A",
            "Latitude": base_lat + 0.02,
            "Longitude": base_lon - 0.02,
            "State": state,
            "Warning Level": 50.0,
            "Danger Level": 60.0,
            "Reliability": "Simulated Fallback",
            "source": "Fallback State Dispersion"
        },
        {
            "GaugeID": f"FALLBACK-{state_key}-2",
            "Station": f"{state} River Monitoring Station B",
            "Latitude": base_lat - 0.02,
            "Longitude": base_lon + 0.02,
            "State": state,
            "Warning Level": 80.0,
            "Danger Level": 95.0,
            "Reliability": "Simulated Fallback",
            "source": "Fallback State Dispersion"
        }
    ]
    return fallback_gauges
