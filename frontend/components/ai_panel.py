"""
ai_panel.py — CivicMind AI Command Center

Fully synchronous Gemini AI panel for Streamlit Cloud compatibility.
Calls Google Gemini 2.5 Flash directly via the sync client.
No asyncio, no backend required. Falls back to rule-based analysis
if GEMINI_API_KEY is not set.
"""
import os
import json
import logging
import streamlit as st
from backend.services.live_data import fetch_weather_sync, fetch_aqi_sync

logger = logging.getLogger("civicmind.ai_panel")


# ──────────────────────────────────────────────────────────────────────────────
# Gemini direct sync call
# ──────────────────────────────────────────────────────────────────────────────

def _gemini_analyze(city: str, weather: dict | None, aqi: dict | None, question: str) -> dict:
    """Call Gemini 2.5 Flash synchronously and return structured JSON report."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return _rule_based_analysis(city, weather, aqi)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        cur_w = (weather or {}).get("current", {})
        cur_a = (aqi    or {}).get("current", {})

        context = f"""
City / State: {city}
Weather Data:
  - Temperature : {cur_w.get('temperature_2m', 'N/A')} °C
  - Humidity    : {cur_w.get('relative_humidity_2m', 'N/A')} %
  - Wind Speed  : {cur_w.get('wind_speed_10m', 'N/A')} km/h
  - Precipitation: {cur_w.get('precipitation', 'N/A')} mm
Air Quality:
  - US AQI      : {cur_a.get('us_aqi', 'N/A')}
  - PM2.5       : {cur_a.get('pm2_5', 'N/A')} µg/m³
  - PM10        : {cur_a.get('pm10', 'N/A')} µg/m³
"""
        prompt = f"""
You are CivicMind AI, an enterprise Smart City Decision Intelligence system.

Telemetry context:
{context}

Operator question: {question or f"Provide a full risk assessment for {city}."}

Respond ONLY with a JSON object using exactly these keys:
{{
  "Risk Level": "Low|Medium|High|Critical",
  "Confidence Score": 0.0-1.0,
  "Priority": "P1|P2|P3",
  "Emergency Level": true|false,
  "Affected Areas": ["area1", "area2"],
  "Evidence": ["observation1", "observation2", "observation3"],
  "Reasoning": "2-3 sentence analytical summary",
  "Recommended Actions": ["action1", "action2", "action3", "action4"],
  "Sources Used": ["Open-Meteo Weather API", "Open-Meteo AQI API", "Gemini 2.5 Flash"]
}}
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1024,
            ),
        )
        raw = response.text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())

    except Exception as exc:
        logger.warning("Gemini call failed: %s — using rule-based fallback", exc)
        return _rule_based_analysis(city, weather, aqi)


# ──────────────────────────────────────────────────────────────────────────────
# Rule-based fallback (always works — no API key needed)
# ──────────────────────────────────────────────────────────────────────────────

def _rule_based_analysis(city: str, weather: dict | None, aqi: dict | None) -> dict:
    cur_w = (weather or {}).get("current", {})
    cur_a = (aqi    or {}).get("current", {})
    temp     = cur_w.get("temperature_2m", 25)
    humidity = cur_w.get("relative_humidity_2m", 60)
    wind     = cur_w.get("wind_speed_10m", 10)
    aqi_val  = cur_a.get("us_aqi", 50)

    score    = 30
    evidence = []
    actions  = []

    if aqi_val > 150:
        score += 25
        evidence.append(f"AQI is {aqi_val} — hazardous air quality posing serious health risks.")
        actions.append("Activate public health advisory. Restrict outdoor activities.")
    elif aqi_val > 100:
        score += 15
        evidence.append(f"AQI is {aqi_val} — unhealthy for sensitive groups.")
        actions.append("Issue advisory for sensitive population groups.")
    else:
        evidence.append(f"AQI is {aqi_val} — within moderate range.")
        actions.append("Maintain routine environmental monitoring.")

    if temp > 38:
        score += 20
        evidence.append(f"Temperature of {temp}°C exceeds heat-stress threshold.")
        actions.append("Issue extreme heat advisory. Deploy cooling centres.")
    elif temp < 8:
        score += 15
        evidence.append(f"Temperature of {temp}°C signals cold-wave conditions.")
        actions.append("Activate cold-wave protocol. Shelter vulnerable populations.")
    else:
        evidence.append(f"Temperature is {temp}°C — within normal operational range.")

    if humidity > 85:
        score += 8
        evidence.append(f"High humidity ({humidity}%) increases heat-index and disease transmission risk.")
        actions.append("Increase vector disease surveillance activities.")

    if wind > 40:
        score += 10
        evidence.append(f"Wind speed of {wind} km/h may disrupt infrastructure and utilities.")
        actions.append("Inspect critical infrastructure for storm readiness.")

    actions.append("Coordinate with district emergency management office.")
    actions.append("Ensure backup communication systems are operational.")

    score = min(score, 100)
    if score >= 75:
        risk, priority, emergency = "Critical", "P1", True
    elif score >= 55:
        risk, priority, emergency = "High",     "P1", False
    elif score >= 35:
        risk, priority, emergency = "Medium",   "P2", False
    else:
        risk, priority, emergency = "Low",      "P3", False

    return {
        "Risk Level":           risk,
        "Confidence Score":     round(0.55 + (score / 400), 2),
        "Priority":             priority,
        "Emergency Level":      emergency,
        "Affected Areas":       [city, "Urban Core", "Peri-urban Districts"],
        "Evidence":             evidence,
        "Reasoning":            (
            f"{city} is currently classified as {risk} risk based on AQI={aqi_val}, "
            f"temperature={temp}°C, and humidity={humidity}%. "
            f"Combined environmental risk score is {score}/100."
        ),
        "Recommended Actions":  actions,
        "Sources Used":         ["Open-Meteo Weather API", "Open-Meteo AQI API", "CivicMind Heuristic Engine"],
    }


# ──────────────────────────────────────────────────────────────────────────────
# Public render function
# ──────────────────────────────────────────────────────────────────────────────

def show_ai_panel(weather: dict | None, aqi: dict | None, city: str, question: str | None = None):

    # ── Shell styling ─────────────────────────────────────────────────────────
    st.markdown(
        """
<style>
details {
    background: #1A1A2E;
    border: 1px solid rgba(0,229,255,0.12);
    border-radius: 10px;
    margin-bottom: 10px;
    padding: 12px 16px;
}
summary {
    font-size: 0.82rem;
    font-weight: 700;
    color: #7ECFDF;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    cursor: pointer;
    outline: none;
    list-style: none;
}
summary::-webkit-details-marker { display: none; }
summary::before { content: "▶  "; font-size: 0.65rem; }
details[open] summary::before { content: "▼  "; }
summary:hover { color: #00E5FF; }
details[open] summary { color: #00E5FF; margin-bottom: 10px; }
</style>
<div style='background:linear-gradient(135deg,#0D1117,#1A1A2E);
            border:1px solid rgba(0,229,255,0.18);
            border-radius:14px;padding:1.5rem;
            box-shadow:0 12px 40px rgba(0,0,0,0.5);'>
<div style='display:flex;align-items:center;gap:10px;margin-bottom:1.2rem;'>
  <div style='width:36px;height:36px;background:linear-gradient(135deg,rgba(0,229,255,0.2),rgba(139,92,246,0.2));
              color:#00E5FF;display:flex;align-items:center;justify-content:center;
              border-radius:10px;font-size:1.2rem;border:1px solid rgba(0,229,255,0.25);'>🤖</div>
  <div>
    <h4 style='margin:0;font-size:1.05rem;color:#fff;'>AI Command Center</h4>
    <span style='font-size:0.73rem;color:#7ECFDF;'>Powered by Gemini 2.5 Flash · Multi-Agent Intelligence</span>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if not question:
        st.markdown(
            "<p style='color:#7ECFDF;font-size:0.88rem;padding:8px 0;'>"
            "Enter a question above and click <b>Analyze</b> to trigger the AI command chain.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Agent progress simulation ─────────────────────────────────────────────
    agents = [
        ("🌦", "Weather Agent",  "#4F8EF7"),
        ("🌫", "AQI Agent",      "#00B8D9"),
        ("🏥", "Hospital Agent", "#37D67A"),
        ("🌊", "Flood Agent",    "#8B5CF6"),
        ("🔮", "Decision Agent", "#F6C445"),
    ]
    bar = st.empty()
    for i, (icon, name, color) in enumerate(agents):
        done = agents[:i + 1]
        remaining = agents[i + 1:]
        html_parts = []
        for ico, n, c in done:
            html_parts.append(
                f"<span style='color:{c};font-size:0.8rem;'>{ico} {n} ✓</span>"
            )
        for ico, n, c in remaining:
            html_parts.append(
                f"<span style='color:#444;font-size:0.8rem;'>{ico} {n}</span>"
            )
        bar.markdown(
            "<div style='display:flex;flex-wrap:wrap;gap:10px 16px;"
            "padding:10px;background:#111;border-radius:8px;margin-bottom:8px;'>"
            + " &nbsp;|&nbsp; ".join(html_parts)
            + "</div>",
            unsafe_allow_html=True,
        )

    # ── Fetch live data (fallback to passed-in data if already fetched) ───────
    if not weather:
        weather = fetch_weather_sync(city)
    if not aqi:
        aqi = fetch_aqi_sync(city)

    # ── Gemini (or rule-based) analysis ───────────────────────────────────────
    with st.spinner("🔮 Synthesizing final decision..."):
        report = _gemini_analyze(city, weather, aqi, question)

    bar.empty()

    # ── Result rendering ──────────────────────────────────────────────────────
    risk_level   = report.get("Risk Level", "Medium")
    conf_score   = report.get("Confidence Score", 0.75)
    priority     = report.get("Priority", "P2")
    reasoning    = report.get("Reasoning", "")
    emerg_level  = report.get("Emergency Level", False)

    risk_colors  = {"Low": "#37D67A", "Medium": "#F6C445", "High": "#FF8A3D", "Critical": "#FF5D73"}
    risk_color   = risk_colors.get(risk_level, "#A5B6D6")

    if emerg_level:
        st.markdown(
            "<div style='background:rgba(255,93,115,0.15);border:1px solid #FF5D73;"
            "border-radius:8px;padding:10px;margin-bottom:12px;color:#FF5D73;"
            "font-weight:bold;font-size:0.85rem;text-align:center;'>"
            "🚨 SYSTEM-WIDE EMERGENCY ALERT ACTIVE</div>",
            unsafe_allow_html=True,
        )

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    kpi_style = "background:#111;border:1px solid rgba(255,255,255,0.06);padding:12px;border-radius:10px;text-align:center;"
    label_style = "font-size:0.72rem;color:#7ECFDF;text-transform:uppercase;letter-spacing:0.05em;"
    val_style_base = "font-size:1.2rem;font-weight:700;"

    with c1:
        st.markdown(
            f"<div style='{kpi_style}'>"
            f"<div style='{label_style}'>Risk Level</div>"
            f"<div style='{val_style_base}color:{risk_color};'>{risk_level}</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div style='{kpi_style}'>"
            f"<div style='{label_style}'>Confidence</div>"
            f"<div style='{val_style_base}color:#00E5FF;'>{int(conf_score * 100)}%</div></div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"<div style='{kpi_style}'>"
            f"<div style='{label_style}'>Priority</div>"
            f"<div style='{val_style_base}color:#F6C445;'>{priority}</div></div>",
            unsafe_allow_html=True,
        )
    with c4:
        affected = ", ".join(map(str, report.get("Affected Areas", [city])[:2]))
        st.markdown(
            f"<div style='{kpi_style}'>"
            f"<div style='{label_style}'>Affected Areas</div>"
            f"<div style='font-size:0.85rem;font-weight:600;color:#fff;'>{affected}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # Expandable details
    evidence_items = "".join(
        f"<li style='margin-bottom:6px;font-size:0.85rem;color:#A5B6D6;'>{e}</li>"
        for e in report.get("Evidence", [])
    )
    action_items = "".join(
        f"<li style='margin-bottom:7px;font-size:0.85rem;color:#fff;'>{a}</li>"
        for a in report.get("Recommended Actions", [])
    )
    sources = "".join(
        f"<span style='background:rgba(255,255,255,0.06);padding:3px 9px;"
        f"border-radius:4px;margin-right:6px;font-size:0.75rem;color:#7ECFDF;'>{s}</span>"
        for s in report.get("Sources Used", [])
    )

    st.markdown(
        f"""
<details>
  <summary>Telemetry Evidence</summary>
  <ul style='margin:10px 0 0 16px;padding:0;'>{evidence_items}</ul>
</details>
<details>
  <summary>Reasoning Protocol</summary>
  <div style='font-size:0.85rem;color:#A5B6D6;line-height:1.6;'>{reasoning}</div>
</details>
<details open>
  <summary>Recommended Action Plan</summary>
  <ul style='margin:10px 0 0 16px;padding:0;'>{action_items}</ul>
</details>
<div style='margin-top:14px;display:flex;flex-wrap:wrap;gap:4px;'>
  <span style='font-size:0.72rem;color:#444;margin-right:4px;'>Data sources:</span>
  {sources}
</div>
</div>
        """,
        unsafe_allow_html=True,
    )