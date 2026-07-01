import streamlit as st
from streamlit_option_menu import option_menu

from config.cities import CITIES


def show_sidebar():

    with st.sidebar:

        st.title("🏙 CivicMind AI")

        st.markdown("---")

        selected_city = st.selectbox(
            "📍 Select City",
            list(CITIES.keys())
        )

        st.markdown("---")

        selected_page = option_menu(
            menu_title=None,
            options=[
                "Dashboard",
                "Decision Center",
                "Analytics",
                "City Intelligence",
                "AI Assistant",
                "Reports",
                "Settings"
            ],
            icons=[
                "house",
                "cpu",
                "bar-chart",
                "geo-alt",
                "robot",
                "file-earmark-text",
                "gear"
            ],
            default_index=0
        )

    return selected_page, selected_city