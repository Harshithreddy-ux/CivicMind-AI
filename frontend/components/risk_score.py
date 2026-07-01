import streamlit as st


def risk_score_panel(weather):

    st.subheader("📊 City Health Score")

    if not weather:
        st.error("Unavailable")
        return

    current = weather["current"]

    temp = current["temperature_2m"]

    humidity = current["relative_humidity_2m"]

    wind = current["wind_speed_10m"]

    score = 100

    if temp > 35:
        score -= 25

    elif temp > 30:
        score -= 10

    if humidity > 80:
        score -= 10

    if wind > 30:
        score -= 15

    score = max(score, 0)

    st.progress(score / 100)

    if score >= 80:
        st.success(f"{score}/100  🟢 GOOD")

    elif score >= 60:
        st.warning(f"{score}/100  🟡 MODERATE")

    else:
        st.error(f"{score}/100  🔴 HIGH RISK")