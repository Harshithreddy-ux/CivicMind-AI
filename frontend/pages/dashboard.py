import streamlit as st

from components.cards import metric_cards
from components.risk_score import show_risk_score
from components.city_status import city_status
from components.ai_panel import show_ai_panel
from components.charts import render_charts
from components.map_view import show_map


def render_dashboard(selected_city, weather, aqi):

    # KPI CARDS
    metric_cards(selected_city)
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # MAP (Visual Centerpiece)
    show_map(selected_city)
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # HEALTH + AI (AI Panel <= 30% width)
    # 70% left, 30% right
    left, right = st.columns([2.3, 1])

    with left:
        show_risk_score(weather, aqi)
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        render_charts(weather, aqi)

    with right:
        show_ai_panel(weather, aqi, selected_city)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # STATUS
    city_status(
        selected_city,
        weather,
        aqi=aqi
    )