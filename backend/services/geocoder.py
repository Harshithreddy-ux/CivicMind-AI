import redis
import json
import random
from typing import Tuple, Optional
from config.cities import CITIES

# Setup Redis connection with a fallback
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=1)
    # Ping to check if alive
    redis_client.ping()
    HAS_REDIS = True
except Exception:
    HAS_REDIS = False
    _MEM_CACHE = {}

def normalize_name(name: str) -> str:
    """Standardizes city, district, or state names for clean joins."""
    if not name:
        return ""
    # Strip whitespace, convert to title case
    return name.strip().lower().title()

def get_coordinates(city: str, address: Optional[str] = None) -> Tuple[float, float]:
    """
    Retrieves coordinates for a location. 
    Checks Redis cache first, then CITIES config, then applies a randomized offset fallback.
    """
    city_norm = normalize_name(city)
    cache_key = f"geo:{city_norm}"
    if address:
        cache_key += f":{normalize_name(address)}"

    # 1. Try Cache
    if HAS_REDIS:
        try:
            cached = redis_client.get(cache_key)
            if cached:
                data = json.loads(cached)
                return float(data["lat"]), float(data["lon"])
        except Exception:
            pass
    else:
        if cache_key in _MEM_CACHE:
            return _MEM_CACHE[cache_key]

    # 2. Get base coordinates from city config
    base_lat = 20.5937  # India center fallback
    base_lon = 78.9629
    
    # Check if city is in our city mapping
    matched_city = None
    for name, info in CITIES.items():
        if normalize_name(name) == city_norm:
            matched_city = info
            break
            
    if matched_city:
        base_lat = matched_city.get("latitude", base_lat)
        base_lon = matched_city.get("longitude", base_lon)

    # 3. Add randomized local dispersion if address or location details are provided
    if address:
        lat = base_lat + random.uniform(-0.04, 0.04)
        lon = base_lon + random.uniform(-0.04, 0.04)
    else:
        lat = base_lat
        lon = base_lon

    # 4. Save to Cache
    coords = (lat, lon)
    if HAS_REDIS:
        try:
            redis_client.set(cache_key, json.dumps({"lat": lat, "lon": lon}), ex=86400 * 30)
        except Exception:
            pass
    else:
        _MEM_CACHE[cache_key] = coords

    return coords
