import streamlit as st
import requests


def get_weather(city):

    try:

        response = requests.get(
            f"http://127.0.0.1:8000/weather?city={city}"
        )

        return response.json()

    except:

        return None


def metric_cards(city):

    weather = get_weather(city)

    if weather and "current" in weather:

        current = weather["current"]

        temperature = f'{current["temperature_2m"]} °C'
        humidity = f'{current["relative_humidity_2m"]}%'
        wind = f'{current["wind_speed_10m"]} km/h'

    else:

        temperature = "--"
        humidity = "--"
        wind = "--"

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("🌡 Temperature", temperature)

    with c2:
        st.metric("💧 Humidity", humidity)

    with c3:
        st.metric("💨 Wind Speed", wind)

    with c4:
        st.metric("🌫 AQI", "Coming Soon")