import os
import json
import re
from typing import Any, Dict

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


class AIService:

    def __init__(self):
        self.model = None
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")

    def _fallback_analysis(self, city_data: Dict[str, Any]) -> Dict[str, Any]:
        weather = city_data.get("weather") or {}
        aqi = city_data.get("aqi") or {}
        current_weather = weather.get("current") or {}
        current_aqi = aqi.get("current") or {}

        temperature = current_weather.get("temperature_2m", 0)
        humidity = current_weather.get("relative_humidity_2m", 0)
        wind = current_weather.get("wind_speed_10m", 0)
        aqi_value = current_aqi.get("us_aqi", 0)

        score = 74
        reasoning = []
        actions = []

        if aqi_value > 150:
            score += 10
            reasoning.append("AQI is above 150, signalling elevated health exposure.")
            actions.append("Reduce outdoor exertion and keep masks ready.")
        elif aqi_value > 100:
            reasoning.append("AQI is elevated but manageable for short outdoor activity.")
            actions.append("Sensitive groups should limit prolonged exposure.")
        else:
            reasoning.append("AQI is within a moderate range.")
            actions.append("Maintain routine outdoor precautions.")

        if temperature > 38:
            score += 8
            reasoning.append("High temperature increases heat stress risk.")
            actions.append("Issue heat precautions and increase hydration support.")
        elif temperature < 10:
            score += 6
            reasoning.append("Cold conditions may increase vulnerability in exposed populations.")
            actions.append("Issue cold-weather guidance for vulnerable residents.")

        if humidity > 80:
            score += 4
            reasoning.append("High humidity can amplify discomfort and health impact.")
            actions.append("Monitor drainage, mosquito risk, and cooling support.")

        if wind > 35:
            score += 4
            reasoning.append("Strong wind may intensify dust and disruption concerns.")
            actions.append("Prepare for transport disruption and dust exposure.")

        if score >= 92:
            risk_level = "HIGH"
        elif score >= 78:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "risk_level": risk_level,
            "summary": f"{city_data.get('city', 'This city')} is showing elevated operational stress from combined weather and air-quality conditions.",
            "recommended_actions": actions[:3],
            "confidence": min(96, max(72, score)),
            "reasoning": reasoning,
            "evidence": [
                f"Temperature: {temperature}°C",
                f"Humidity: {humidity}%",
                f"Wind: {wind} km/h",
                f"AQI: {aqi_value}"
            ]
        }

    def analyze_city(self, city_data):
        if self.model is None:
            return self._fallback_analysis(city_data)

        question = city_data.get("question")
        question_text = f"User Question: {question}\n\n" if question else ""

        prompt = f"""
You are CivicMind AI, an expert Smart City Decision Intelligence system.

{question_text}Analyze the following city information:

City Data:
{city_data}

Based on the data and the user question (if any), return ONLY a valid JSON object matching exactly this schema:
{{
    "risk_level": "LOW",
    "summary": "Your analysis summary here",
    "recommended_actions": ["Action 1", "Action 2", "Action 3"],
    "confidence": 85,
    "evidence": ["Evidence 1", "Evidence 2"]
}}

Note: risk_level must be one of LOW, MEDIUM, HIGH. confidence must be an integer between 0 and 100.
"""

        try:
            response = self.model.generate_content(prompt)
            content = response.text
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return self._fallback_analysis(city_data)
        except Exception:
            return self._fallback_analysis(city_data)