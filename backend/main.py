from fastapi import FastAPI, HTTPException

from backend.services.weather_service import WeatherService
from config.cities import CITIES

app = FastAPI(
    title="CivicMind AI",
    version="1.0.0"
)

weather_service = WeatherService()


@app.get("/")
def home():
    return {
        "status": "Running",
        "project": "CivicMind AI"
    }


@app.get("/cities")
def cities():
    return list(CITIES.keys())


@app.get("/weather")
def weather(city: str = "Bengaluru"):

    data = weather_service.get_weather(city)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="City not supported."
        )

    return data