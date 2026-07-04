import streamlit as st
from streamlit_option_menu import option_menu

from config.cities import CITIES

from components.branding import get_branding_html

def show_sidebar():
    with st.sidebar:
        st.markdown(
            f"<div class='sidebar-shell'>{get_branding_html()}</div>",
            unsafe_allow_html=True
        )

        selected_city = st.selectbox(
            "📍 Operating City",
            list(CITIES.keys()),
            help="Select the region to analyze"
        )
        # Premium option menu configuration
        selected_page = option_menu(
            menu_title=None,
            options=[
                "Dashboard",
                "Analytics",
                "City Intelligence",
                "Forecast",
                "AI Assistant",
                "Reports",
                "Settings"
            ],
            icons=[
                "grid-1x2",
                "graph-up-arrow",
                "map",
                "cloud-sun",
                "cpu",
                "file-text",
                "sliders"
            ],
            default_index=0,
            styles={
                "container": {
                    "padding": "0.5rem", 
                    "background": "transparent",
                    "border": "none"
                },
                "nav-link": {
                    "font-size": "0.95rem", 
                    "font-weight": "500",
                    "margin": "0.25rem 0", 
                    "border-radius": "8px", 
                    "color": "#A5B6D6",
                    "transition": "all 0.3s ease",
                    "padding": "0.6rem 1rem"
                },
                "icon": {
                    "font-size": "1.1rem",
                    "margin-right": "0.75rem"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, rgba(94, 231, 255, 0.15), rgba(139, 92, 246, 0.15))", 
                    "color": "#FFFFFF",
                    "border-left": "3px solid #5EE7FF",
                    "font-weight": "600"
                },
            },
        )

    return selected_page, selected_city