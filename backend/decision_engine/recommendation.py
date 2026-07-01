def generate_recommendation(weather, aqi=None):

    if not weather:
        return {
            "risk": "Unknown",
            "recommendation": "Weather information unavailable.",
            "confidence": "0%"
        }

    current = weather.get("current", {})

    temp = current.get("temperature_2m", 0)
    humidity = current.get("relative_humidity_2m", 0)
    wind = current.get("wind_speed_10m", 0)

    recommendations = []

    risk = "Low"

    if temp >= 35:
        risk = "High"
        recommendations.append("Issue a heat advisory.")
        recommendations.append("Increase drinking water stations.")

    elif temp >= 30:
        risk = "Medium"
        recommendations.append("Monitor outdoor public events.")

    if humidity >= 80:
        recommendations.append("Monitor drainage and mosquito breeding.")

    if wind >= 25:
        recommendations.append("Prepare alerts for strong wind conditions.")

    if not recommendations:
        recommendations.append("Current city conditions are stable.")

    return {
        "risk": risk,
        "recommendation": recommendations,
        "confidence": "94%"
    }   