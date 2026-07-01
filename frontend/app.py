import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from components.sidebar import show_sidebar
from components.cards import metric_cards, get_weather_data
from components.city_status import city_status
from components.recommendation import recommendation_panel
from components.map_view import show_map
from components.risk_score import risk_score_panel

st.set_page_config(
    page_title="CivicMind AI",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_css():

    css = ROOT / "frontend" / "styles" / "style.css"

    if css.exists():

        with open(css, "r", encoding="utf-8") as f:

            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )


load_css()

selected_page, selected_city = show_sidebar()

st.title("🏙️ CivicMind AI")

st.caption(
    "AI-Powered Decision Intelligence Platform for Smart Communities"
)

st.divider()

metric_cards(selected_city)

weather = get_weather_data(selected_city)
risk_score_panel(weather)

left, right = st.columns([2, 1])

with left:
    city_status(selected_city, weather)

with right:
    recommendation_panel(selected_city)

st.divider()

show_map(selected_city)

st.divider()

st.subheader(selected_page)

st.info(
    "🚀 Live Decision Intelligence Dashboard"
)

st.caption(
    "© 2026 CivicMind AI | Google Cloud APAC Hackathon"
)