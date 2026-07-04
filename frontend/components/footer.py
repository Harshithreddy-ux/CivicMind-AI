import streamlit as st
from datetime import datetime


def render_footer():

    current_time = datetime.now().strftime("%d %b %Y  •  %I:%M %p")

    st.markdown(
        f"""
<div class="cm-footer">
    <div class="cm-footer-left">
        <h4>CivicMind AI</h4>
        <p>
            AI Powered Decision Intelligence Platform
            for Smart Cities and Emergency Operations
        </p>
    </div>
    <div class="cm-footer-center">
        <div class="footer-status">
            <span class="status-dot"></span>
            <span>System Operational</span>
        </div>
        <div class="footer-time">
            Last Updated
            <strong>{current_time}</strong>
        </div>
    </div>
    <div class="cm-footer-right">
        <div class="footer-version">
            Version 2.0
        </div>
        <div class="footer-copy">
            © 2026 CivicMind AI
        </div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )