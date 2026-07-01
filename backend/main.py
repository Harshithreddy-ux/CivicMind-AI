from fastapi import FastAPI, HTTPException

from backend.services.weather_service import WeatherService
from backend.data_sources.aqi_api import AQIAPI
from backend.decision_engine.recommendation import generate_recommendation
from config.cities import CITIES

# ======================================================
# FastAPI
# ======================================================

app = FastAPI(
    title="CivicMind AI",
    version="1.0.0"
)

weather_service = WeatherService()
aqi_service = AQIAPI()

# ======================================================
# Root
# ======================================================

@app.get("/")
def home():

    return {
        "status": "Running",
        "project": "CivicMind AI",
        "version": "1.0.0"
    }

# ======================================================
# Cities
# ======================================================

@app.get("/cities")
def cities():

    return list(CITIES.keys())

# ======================================================
# Weather
# ======================================================

@app.get("/weather")
def weather(city: str = "Bengaluru"):

    weather_data = weather_service.get_weather(city)

    if weather_data is None:
        raise HTTPException(
            status_code=404,
            detail="City not supported."
        )

    return weather_data

# ======================================================
# AQI
# ======================================================

@app.get("/aqi")
def aqi(city: str = "Bengaluru"):

    aqi_data = aqi_service.get_aqi(city)

    if aqi_data is None:
        raise HTTPException(
            status_code=404,
            detail="AQI unavailable."
        )

    return aqi_data

# ======================================================
# AI Recommendation
# ======================================================

@app.get("/recommendation")
def recommendation(city: str = "Bengaluru"):

    weather_data = weather_service.get_weather(city)

    if weather_data is None:
        raise HTTPException(
            status_code=404,
            detail="Weather unavailable."
        )

    return generate_recommendation(weather_data)