import streamlit as st
from datetime import datetime


def city_status(city, weather):

    st.subheader("🌍 City Status")

    if weather and "current" in weather:

        current = weather["current"]

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**City:** {city}")
            st.write(f"**Temperature:** {current['temperature_2m']} °C")
            st.write(f"**Humidity:** {current['relative_humidity_2m']} %")

        with col2:
            st.write(f"**Wind Speed:** {current['wind_speed_10m']} km/h")
            st.write("**Status:** 🟢 Online")
            st.write(
                f"**Updated:** {datetime.now().strftime('%H:%M:%S')}"
            )

    else:

        st.warning("Weather service unavailable.")