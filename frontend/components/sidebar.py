from streamlit_option_menu import option_menu
import streamlit as st

def show_sidebar():
    with st.sidebar:
        selected = option_menu(
            menu_title="CivicMind AI",
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
            menu_icon="building",
            default_index=0,
        )

    return selected