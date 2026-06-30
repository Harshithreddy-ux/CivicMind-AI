import streamlit as st
from components.sidebar import show_sidebar

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="CivicMind AI",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Load Custom CSS
# -----------------------------
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

local_css("frontend/styles/style.css")

# -----------------------------
# Sidebar
# -----------------------------
selected = show_sidebar()

# -----------------------------
# Header
# -----------------------------
st.title("🏙️ CivicMind AI")

st.caption(
    "AI-Powered Decision Intelligence Platform for Smart Communities"
)

st.divider()

# -----------------------------
# Current Page
# -----------------------------
st.subheader(f"📍 {selected}")

st.write(
    "Welcome to CivicMind AI. This platform helps governments, "
    "communities, organizations, and citizens make better decisions "
    "using real-world data and Artificial Intelligence."
)

st.divider()

# -----------------------------
# Temporary Placeholder
# -----------------------------
st.info(
    "🚀 Dashboard components, live datasets, AI agents, and analytics "
    "will be integrated in the next development phase."
)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")

st.caption(
    "© 2026 CivicMind AI | Google Cloud APAC Hackathon | Decision Intelligence Platform"
)