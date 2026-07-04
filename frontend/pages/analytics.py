import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.dataset_service import get_city_facilities, get_city_population, get_city_rainfall, get_city_trend_series


def render_analytics(selected_city, weather, aqi):
    st.markdown("## Analytics")
    st.caption("Interactive city analytics for weather, AQI, population, crime, flood, and healthcare trends.")

    population = get_city_population(selected_city)
    rainfall = get_city_rainfall(selected_city)
    hospitals = get_city_facilities(selected_city, "hospitals")
    trend_series = get_city_trend_series(selected_city)

    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("Population", f"{population:,}" if population is not None else "N/A")
    with metric_cols[1]:
        st.metric("Rainfall", f"{rainfall:.1f} mm" if rainfall is not None else "N/A")
    with metric_cols[2]:
        st.metric("Hospitals", len(hospitals))
    with metric_cols[3]:
        aqi_value = aqi["current"]["us_aqi"] if aqi and aqi.get("current") else "N/A"
        st.metric("AQI", aqi_value)

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=trend_series["temperature"], mode="lines+markers", name="Temperature", line=dict(color="#4fd1ff", width=2)))
    fig.add_trace(go.Scatter(y=trend_series["aqi"], mode="lines+markers", name="AQI", line=dict(color="#fb7185", width=2)))
    fig.add_trace(go.Scatter(y=trend_series["humidity"], mode="lines+markers", name="Humidity", line=dict(color="#35d399", width=2)))
    fig.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, width='stretch')

    chart_cols = st.columns(2)
    with chart_cols[0]:
        rain_fig = go.Figure(data=go.Scatter(y=trend_series["rainfall"], mode="lines+markers", name="Rainfall", line=dict(color="#8b5cf6", width=2)))
        rain_fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(rain_fig, width='stretch')
    with chart_cols[1]:
        pop_fig = go.Figure(data=go.Scatter(y=trend_series["population"], mode="lines+markers", name="Population", line=dict(color="#fbbf24", width=2)))
        pop_fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(pop_fig, width='stretch')

    crime_fig = go.Figure(data=go.Scatter(y=trend_series["crime"], mode="lines+markers", name="Crime", line=dict(color="#fb7185", width=2)))
    crime_fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(crime_fig, width='stretch')

    flood_fig = go.Figure(data=go.Scatter(y=trend_series["flood"], mode="lines+markers", name="Flood", line=dict(color="#4fd1ff", width=2)))
    flood_fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(flood_fig, width='stretch')

    st.subheader("Facility coverage")
    if hospitals:
        df = pd.DataFrame(hospitals)
        st.dataframe(df[["Hospital"]].head(10), width='stretch')
    else:
        st.info("No hospital records are available for this city in the local dataset.")
