"""
Synchronous weather + AQI fetcher for Streamlit Cloud compatibility.
Uses httpx.get() (sync) — works in any thread without an event loop.
"""
import httpx
import os
import logging
from config.cities import CITIES

logger = logging.getLogger("civicmind.live")

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AQI_URL     = "https://air-quality-api.open-meteo.com/v1/air-quality"


def _get_coords(city: str):
    info = CITIES.get(city)
    if not info:
        return None, None
    return info["latitude"], info["longitude"]


def fetch_weather_sync(city: str) -> dict | None:
    """
    Fetch real-time weather for a city using synchronous HTTPX.
    Returns None on any failure — caller must handle gracefully.
    """
    lat, lon = _get_coords(city)
    if lat is None:
        return None
    try:
        resp = httpx.get(
            WEATHER_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "wind_speed_10m",
                    "precipitation",
                ],
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                ],
                "forecast_days": 7,
                "timezone": "auto",
            },
            timeout=12.0,
        )
        resp.raise_for_status()
        data = resp.json()
        # Sanity check – ensure 'current' key present
        if "current" not in data:
            return None
        return data
    except Exception as exc:
        logger.warning("Weather fetch failed for %s: %s", city, exc)
        return None


def fetch_aqi_sync(city: str) -> dict | None:
    """
    Fetch real-time AQI for a city using synchronous HTTPX.
    Returns None on any failure — caller must handle gracefully.
    """
    lat, lon = _get_coords(city)
    if lat is None:
        return None
    try:
        resp = httpx.get(
            AQI_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "us_aqi",
                    "pm10",
                    "pm2_5",
                    "carbon_monoxide",
                    "nitrogen_dioxide",
                ],
            },
            timeout=12.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if "current" not in data:
            return None
        return data
    except Exception as exc:
        logger.warning("AQI fetch failed for %s: %s", city, exc)
        return None
