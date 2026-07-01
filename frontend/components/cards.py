import streamlit as st
import requests


# ======================================================
# Get Weather Data from Backend
# ======================================================
def get_weather(city):

    try:
        response = requests.get(
            f"http://127.0.0.1:8000/weather?city={city}",
            timeout=5
        )

        if response.status_code == 200:
            return response.json()

    except Exception:
        pass

    return None


# ======================================================
# Return Raw Weather Object
# ======================================================
def get_weather_data(city):

    return get_weather(city)


# ======================================================
# Dashboard KPI Cards
# ======================================================
def metric_cards(city):

    weather = get_weather(city)

    if weather and "current" in weather:

        current = weather["current"]

        temperature = f"{current['temperature_2m']} °C"
        humidity = f"{current['relative_humidity_2m']} %"
        wind = f"{current['wind_speed_10m']} km/h"

    else:

        temperature = "--"
        humidity = "--"
        wind = "--"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🌡 Temperature",
            value=temperature
        )

    with col2:
        st.metric(
            label="💧 Humidity",
            value=humidity
        )

    with col3:
        st.metric(
            label="💨 Wind Speed",
            value=wind
        )

    with col4:
        st.metric(
            label="🌫 AQI",
            value="Coming Soon"
        )