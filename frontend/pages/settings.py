import streamlit as st

def render_settings():
    st.markdown("## Settings")
    st.caption("Control the operational appearance and connectivity for CivicMind AI.")

    # 1. Appearance Section
    with st.container(border=True):
        st.markdown("### Operational Theme")
        theme = st.radio("Theme Mode", ["Dark (Default/Premium)", "Light Mode"], horizontal=True)
        st.session_state["theme"] = "Dark" if "Dark" in theme else "Light"

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 2. System Status Badges
    st.markdown("### System Telemetry Status")
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown(
                """
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <b style='font-size:0.85rem; color:#fff;'>Google Gemini</b><br>
                        <span style='font-size:0.72rem; color:#A5B6D6;'>Agent Consensus</span>
                    </div>
                    <span style='background:rgba(61,220,151,0.12); color:#3DDC97; font-size:0.68rem; padding:3px 8px; border-radius:12px; font-weight:600;'>● ACTIVE</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    with c2:
        with st.container(border=True):
            st.markdown(
                """
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <b style='font-size:0.85rem; color:#fff;'>SQLite Engine</b><br>
                        <span style='font-size:0.72rem; color:#A5B6D6;'>Ingestion Layer</span>
                    </div>
                    <span style='background:rgba(61,220,151,0.12); color:#3DDC97; font-size:0.68rem; padding:3px 8px; border-radius:12px; font-weight:600;'>● ACTIVE</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    with c3:
        with st.container(border=True):
            st.markdown(
                """
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <b style='font-size:0.85rem; color:#fff;'>Weather/AQI API</b><br>
                        <span style='font-size:0.72rem; color:#A5B6D6;'>External Telemetry</span>
                    </div>
                    <span style='background:rgba(61,220,151,0.12); color:#3DDC97; font-size:0.68rem; padding:3px 8px; border-radius:12px; font-weight:600;'>● ACTIVE</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 3. Control Toggles
    with st.container(border=True):
        st.markdown("### Operational Controls")
        col_l, col_r = st.columns(2)
        with col_l:
            st.checkbox("Enable Real-Time Sensor WebSocket listener", value=True)
            st.checkbox("Write SQLite indexes to memory cache", value=True)
        with col_r:
            st.checkbox("Log Agent processing latencies", value=True)
            st.checkbox("Enable client-side compression", value=True)
