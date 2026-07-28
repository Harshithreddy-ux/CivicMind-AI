"""
cards.py — Weather & AQI metric card components for Streamlit.

Uses the synchronous live_data fetcher so it works correctly on
Streamlit Community Cloud (no event-loop conflicts).
"""
import streamlit as st
from backend.services.live_data import fetch_weather_sync, fetch_aqi_sync


# ──────────────────────────────────────────────────────────────
# Cached data fetchers  (5-min TTL keeps the UI snappy)
# ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def get_weather(city: str) -> dict | None:
    return fetch_weather_sync(city)


@st.cache_data(ttl=300, show_spinner=False)
def get_aqi(city: str) -> dict | None:
    return fetch_aqi_sync(city)


def get_weather_data(city: str) -> dict | None:
    """Alias used by app.py load_city_context."""
    return get_weather(city)


# ──────────────────────────────────────────────────────────────
# Internal card renderer
# ──────────────────────────────────────────────────────────────

def _card(icon: str, title: str, value: str, subtitle: str, color: str):
    st.markdown(
        f"""
        <div class="cm-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div class="cm-title">{title}</div>
                    <div class="cm-value">{value}</div>
                    <div class="cm-sub" style="color:{color};">{subtitle}</div>
                </div>
                <div class="cm-icon"
                     style="background:linear-gradient(135deg,{color},rgba(255,255,255,0.1));">
                    {icon}
                </div>
            </div>
            <div class="sparkline">
                <span style="background:linear-gradient(180deg,{color},transparent);animation-delay:0s;"></span>
                <span style="background:linear-gradient(180deg,{color},transparent);animation-delay:0.2s;"></span>
                <span style="background:linear-gradient(180deg,{color},transparent);animation-delay:0.4s;"></span>
                <span style="background:linear-gradient(180deg,{color},transparent);animation-delay:0.1s;"></span>
                <span style="background:linear-gradient(180deg,{color},transparent);animation-delay:0.5s;"></span>
                <span style="background:linear-gradient(180deg,{color},transparent);animation-delay:0.3s;"></span>
                <span style="background:linear-gradient(180deg,{color},transparent);animation-delay:0.6s;"></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────
# Public: KPI metric card row
# ──────────────────────────────────────────────────────────────

def metric_cards(city: str):
    weather = get_weather(city)
    aqi     = get_aqi(city)

    # ── Weather fields ────────────────────────────────────────
    temp = wind = hum = "--"
    if weather and "current" in weather:
        cur  = weather["current"]
        temp = f"{cur.get('temperature_2m', '--')}°C"
        hum  = f"{cur.get('relative_humidity_2m', '--')}%"
        wind = f"{cur.get('wind_speed_10m', '--')} km/h"

    # ── AQI fields ────────────────────────────────────────────
    aqi_value = "--"
    aqi_text  = "Unavailable"
    aqi_color = "#4F8EF7"

    if aqi and "current" in aqi:
        raw = aqi["current"].get("us_aqi")
        if raw is not None:
            aqi_value = int(raw)
            if aqi_value <= 50:
                aqi_text, aqi_color = "Good",      "#37D67A"
            elif aqi_value <= 100:
                aqi_text, aqi_color = "Moderate",  "#F6C445"
            elif aqi_value <= 150:
                aqi_text, aqi_color = "Poor",      "#FF8A3D"
            else:
                aqi_text, aqi_color = "Hazardous", "#FF5C75"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _card("🌡", "Temperature", str(temp),       "Live Weather",  "#4F8EF7")
    with c2:
        _card("💧", "Humidity",    str(hum),         "Atmospheric",   "#00B8D9")
    with c3:
        _card("💨", "Wind",        str(wind),        "Surface Wind",  "#7C4DFF")
    with c4:
        _card("🌫", "AQI",         str(aqi_value),   aqi_text,        aqi_color)


# ──────────────────────────────────────────────────────────────
# Expose BACKEND for legacy ai_panel import
# ──────────────────────────────────────────────────────────────
import os
BACKEND = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")