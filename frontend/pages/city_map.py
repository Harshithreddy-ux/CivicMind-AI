import streamlit as st

from components.map_view import show_map


def render_city_map(selected_city):
    st.markdown("## City Intelligence")
    st.caption("Population, facilities, flood risk, and emergency services overview.")
    show_map(selected_city)
    st.info("The map includes hospitals, emergency facilities, and city markers for rapid situational awareness.")
