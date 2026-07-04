import streamlit as st


def render_settings():
    st.markdown("## Settings")
    st.caption("Control the operational appearance and connectivity for CivicMind AI.")

    theme = st.radio("Theme", ["Dark", "Light"], horizontal=True)
    st.session_state["theme"] = theme

    st.subheader("System status")
    status_items = [
        ("Google Cloud", "Connected"),
        ("NVIDIA", "Connected"),
        ("Weather API", "Connected"),
        ("AQI API", "Connected"),
        ("Dataset Status", "Cached locally"),
    ]
    for item, value in status_items:
        st.write(f"- **{item}**: {value}")
