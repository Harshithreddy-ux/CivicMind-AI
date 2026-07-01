import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import streamlit as st

from components.sidebar import show_sidebar
from components.cards import metric_cards


st.set_page_config(
    page_title="CivicMind AI",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_css():
    try:
        with open("frontend/styles/style.css") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )
    except:
        pass


load_css()

selected_page, selected_city = show_sidebar()

st.title("🏙️ CivicMind AI")

st.caption(
    "AI-Powered Decision Intelligence Platform for Smart Communities"
)

st.divider()

metric_cards(selected_city)

st.divider()

st.subheader(f"📍 {selected_page}")

st.caption(f"Currently Monitoring : {selected_city}")

st.write("""
Welcome to **CivicMind AI**

AI Powered Decision Intelligence Platform
for Governments, Communities and Citizens.
""")

st.info(
    "🚀 Live datasets, analytics, AI recommendations and forecasting will appear here."
)

st.divider()

st.caption(
    "© 2026 CivicMind AI | Google Cloud APAC Hackathon"
)