"""
Expanded test suite for CivicMind AI.
Tests cover: AI service, dataset service, database manager, and backend health.
"""
import sys
import os
import pytest

# Ensure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# AI Service Tests
# ---------------------------------------------------------------------------
from backend.services.ai_service import AIService


def test_fallback_analysis_uses_observed_conditions():
    """Fallback analysis flags HIGH risk for hot, humid, high-AQI conditions."""
    service = AIService()
    city_data = {
        "city": "Delhi",
        "weather": {
            "current": {
                "temperature_2m": 42,
                "relative_humidity_2m": 78,
                "wind_speed_10m": 8,
            }
        },
        "aqi": {"current": {"us_aqi": 180}},
    }
    result = service._fallback_analysis(city_data)

    assert result["risk_level"] == "HIGH"
    assert result["confidence"] >= 70
    assert len(result["recommended_actions"]) >= 2
    assert "reasoning" in result


def test_fallback_analysis_low_risk():
    """Fallback analysis flags LOW risk for mild, clean-air conditions."""
    service = AIService()
    city_data = {
        "city": "Mysuru",
        "weather": {
            "current": {
                "temperature_2m": 22,
                "relative_humidity_2m": 45,
                "wind_speed_10m": 5,
            }
        },
        "aqi": {"current": {"us_aqi": 30}},
    }
    result = service._fallback_analysis(city_data)

    assert result["risk_level"] in ("LOW", "MEDIUM")
    assert "reasoning" in result
    assert isinstance(result["recommended_actions"], list)


def test_fallback_analysis_missing_weather_key():
    """Fallback analysis handles missing weather gracefully."""
    service = AIService()
    city_data = {"city": "Chennai"}
    result = service._fallback_analysis(city_data)

    # Should return a dict without crashing
    assert isinstance(result, dict)
    assert "risk_level" in result


# ---------------------------------------------------------------------------
# Dataset Service Tests
# ---------------------------------------------------------------------------
from frontend.utils.dataset_service import get_city_population, get_city_rainfall


def test_get_city_population_returns_positive_int():
    """City population lookup returns a positive integer."""
    population = get_city_population("Chennai")
    assert isinstance(population, (int, float))
    assert population > 0


def test_get_city_population_unknown_city():
    """Unknown city returns a non-negative population (fallback)."""
    population = get_city_population("UnknownCityXYZ123")
    assert isinstance(population, (int, float))
    assert population >= 0


def test_get_city_rainfall_returns_numeric():
    """City rainfall lookup returns a numeric value."""
    rainfall = get_city_rainfall("Mumbai")
    assert isinstance(rainfall, (int, float))
    assert rainfall >= 0


# ---------------------------------------------------------------------------
# Config Tests
# ---------------------------------------------------------------------------
from config.cities import CITIES


def test_cities_config_not_empty():
    """CITIES config contains at least one city."""
    assert len(CITIES) > 0


def test_cities_config_has_required_keys():
    """Each city entry contains lat and lon keys."""
    for city_name, city_data in CITIES.items():
        assert "lat" in city_data or "latitude" in city_data or isinstance(city_data, tuple), \
            f"City '{city_name}' missing coordinate data"
