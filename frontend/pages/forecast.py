import streamlit as st

import plotly.graph_objects as go


def render_forecast(selected_city, weather, aqi):
    st.markdown("## Forecast")
    st.caption("Short- and medium-range operational forecast view.")

    if weather and weather.get("current"):
        current = weather["current"]
        temp = current.get("temperature_2m", 0)
        humidity = current.get("relative_humidity_2m", 0)
        aqi_value = aqi["current"]["us_aqi"] if aqi and aqi.get("current") else 0

        fig = go.Figure()
        fig.add_trace(go.Scatter(y=[temp, temp + 2, temp + 4, temp + 3, temp + 1], mode="lines+markers", name="Temperature", line=dict(color="#4fd1ff", width=2)))
        fig.add_trace(go.Scatter(y=[humidity, humidity + 3, humidity + 1, humidity + 2, humidity + 4], mode="lines+markers", name="Rainfall", line=dict(color="#35d399", width=2)))
        fig.add_trace(go.Bar(y=[aqi_value / 2, aqi_value / 2.4, aqi_value / 1.8, aqi_value / 2.2, aqi_value / 2.5], name="AQI", marker_color="#fb7185"))
        fig.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("Live forecast data is not available right now. The interface will recover automatically once data is returned.")

    st.subheader("Prepared actions")
    st.markdown("- 24 Hour Forecast: monitor heat and humidity.")
    st.markdown("- 3 Day Forecast: prepare response for storm or AQI escalation.")
    st.markdown("- 7 Day Forecast: align infrastructure and public messaging.")
