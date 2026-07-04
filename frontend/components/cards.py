import requests
import streamlit as st


BACKEND = "http://127.0.0.1:8000"


# ======================================================
# WEATHER
# ======================================================

@st.cache_data(ttl=300)
def get_weather(city):

    try:

        response = requests.get(
            f"{BACKEND}/weather",
            params={"city": city},
            timeout=5,
        )

        if response.status_code == 200:
            return response.json()

    except Exception:
        pass

    return None


# ======================================================
# AQI
# ======================================================

@st.cache_data(ttl=300)
def get_aqi(city):

    try:

        response = requests.get(
            f"{BACKEND}/aqi",
            params={"city": city},
            timeout=5,
        )

        if response.status_code == 200:
            return response.json()

    except Exception:
        pass

    return None


# ======================================================
# SHARED WEATHER OBJECT
# ======================================================

def get_weather_data(city):

    return get_weather(city)


# ======================================================
# CARD
# ======================================================

def _card(icon, title, value, subtitle, color):
    st.markdown(
        f"""
        <div class="cm-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div class="cm-title">{title}</div>
                    <div class="cm-value">{value}</div>
                    <div class="cm-sub" style="color: {color};">{subtitle}</div>
                </div>
                <div class="cm-icon" style="background: linear-gradient(135deg, {color}, rgba(255,255,255,0.1));">
                    {icon}
                </div>
            </div>
            <div class="sparkline">
                <span style="background: linear-gradient(180deg, {color}, transparent); animation-delay: 0s;"></span>
                <span style="background: linear-gradient(180deg, {color}, transparent); animation-delay: 0.2s;"></span>
                <span style="background: linear-gradient(180deg, {color}, transparent); animation-delay: 0.4s;"></span>
                <span style="background: linear-gradient(180deg, {color}, transparent); animation-delay: 0.1s;"></span>
                <span style="background: linear-gradient(180deg, {color}, transparent); animation-delay: 0.5s;"></span>
                <span style="background: linear-gradient(180deg, {color}, transparent); animation-delay: 0.3s;"></span>
                <span style="background: linear-gradient(180deg, {color}, transparent); animation-delay: 0.6s;"></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ======================================================
# KPI CARDS
# ======================================================

def metric_cards(city):

    weather = get_weather(city)

    aqi = get_aqi(city)

    temp = "--"

    hum = "--"

    wind = "--"

    aqi_value = "--"

    aqi_text = "Unavailable"

    if weather and "current" in weather:

        current = weather["current"]

        temp = f"{current['temperature_2m']}°C"

        hum = f"{current['relative_humidity_2m']}%"

        wind = f"{current['wind_speed_10m']} km/h"

    if aqi and "current" in aqi:

        aqi_value = aqi["current"]["us_aqi"]

        if aqi_value <= 50:

            aqi_text = "Good"

            aqi_color = "#37D67A"

        elif aqi_value <= 100:

            aqi_text = "Moderate"

            aqi_color = "#F6C445"

        elif aqi_value <= 150:

            aqi_text = "Poor"

            aqi_color = "#FF8A3D"

        else:

            aqi_text = "Hazardous"

            aqi_color = "#FF5C75"

    else:

        aqi_color = "#4F8EF7"

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        _card(

            "🌡",

            "Temperature",

            temp,

            "Live Weather",

            "#4F8EF7",

        )

    with c2:

        _card(

            "💧",

            "Humidity",

            hum,

            "Atmospheric",

            "#00B8D9",

        )

    with c3:

        _card(

            "💨",

            "Wind",

            wind,

            "Surface Wind",

            "#7C4DFF",

        )

    with c4:

        _card(

            "🌫",

            "AQI",

            str(aqi_value),

            aqi_text,

            aqi_color,

        )