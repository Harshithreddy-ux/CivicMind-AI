from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class CurrentAQI(BaseModel):
    time: str
    interval: int
    us_aqi: float

class AQIResponse(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    current_units: Dict[str, str]
    current: CurrentAQI
