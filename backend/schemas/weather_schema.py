from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class CurrentWeather(BaseModel):
    time: str
    interval: int
    temperature_2m: float
    relative_humidity_2m: float
    apparent_temperature: float
    wind_speed_10m: float
    precipitation: float

class DailyWeather(BaseModel):
    time: List[str]
    temperature_2m_max: List[float]
    temperature_2m_min: List[float]
    precipitation_sum: List[float]

class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    current_units: Dict[str, str]
    current: CurrentWeather
    daily_units: Dict[str, str]
    daily: DailyWeather
