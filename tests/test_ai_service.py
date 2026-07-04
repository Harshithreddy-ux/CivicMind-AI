from backend.services.ai_service import AIService


def test_fallback_analysis_uses_observed_conditions():
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
        "aqi": {
            "current": {"us_aqi": 180}
        },
    }

    result = service._fallback_analysis(city_data)

    assert result["risk_level"] == "HIGH"
    assert result["confidence"] >= 70
    assert len(result["recommended_actions"]) >= 2
    assert "reasoning" in result
