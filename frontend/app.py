import sys
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
FRONTEND_ROOT = ROOT / "frontend"

for path in (str(ROOT), str(FRONTEND_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from components.cards import get_weather_data
from components.footer import render_footer
from components.sidebar import show_sidebar
from pages.analytics import render_analytics
from pages.assistant import render_assistant
from pages.city_map import render_city_map
from pages.dashboard import render_dashboard
from pages.forecast import render_forecast
from pages.reports import render_reports
from pages.settings import render_settings
from utils.dataset_service import load_all_datasets
from components.branding import get_logo_src
import threading
import json

logo_src = get_logo_src()
LOGO_PATH = str(Path(__file__).resolve().parent.parent / "assets" / "logo.svg")

# Thread-safe WebSocket Background Alert Listener
def start_alert_listener():
    import asyncio
    
    async def ws_client():
        import websockets
        uri = "ws://127.0.0.1:8000/ws/alerts"
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    while True:
                        msg = await websocket.recv()
                        data = json.loads(msg)
                        if "alerts" not in st.session_state:
                            st.session_state.alerts = []
                        st.session_state.alerts.append(data)
                        st.rerun()
            except Exception:
                await asyncio.sleep(5)  # Reconnect cooldown

    def run_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(ws_client())

    if "alert_listener_started" not in st.session_state:
        st.session_state.alert_listener_started = True
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=run_loop, args=(loop,), daemon=True)
        t.start()

st.set_page_config(
    page_title="CivicMind AI",
    page_icon=LOGO_PATH,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.set_option("client.showSidebarNavigation", False)


def load_css():
    try:
        with open("frontend/styles/style.css", encoding="utf-8") as handle:
            st.markdown(f"<style>{handle.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass


@st.cache_data(show_spinner=False)
def load_city_context(city: str):
    weather = get_weather_data(city)
    aqi = None
    try:
        response = requests.get(f"http://127.0.0.1:8000/aqi?city={city}", timeout=5)
        if response.status_code == 200:
            aqi = response.json()
    except Exception:
        pass
    return weather, aqi


load_css()
load_all_datasets()
start_alert_listener()

if "alerts" in st.session_state and st.session_state.alerts:
    while st.session_state.alerts:
        alert = st.session_state.alerts.pop(0)
        st.toast(
            f"🚨 LIVE ALERT [{alert['city'].upper()}]: {alert['sensor_type'].upper()} level is {alert['value']} {alert['unit']}",
            icon="🚨"
        )

if "ui_ready" not in st.session_state:
    st.session_state.ui_ready = False

if not st.session_state.ui_ready:
    placeholder = st.empty()
    placeholder.markdown(
        """
        <div class='loading-shell'>
            <h1>CivicMind AI</h1>
            <p>Initializing enterprise platform…</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    placeholder.empty()
    st.session_state.ui_ready = True

selected_page, selected_city = show_sidebar()
weather, aqi = load_city_context(selected_city)

if "selected_city" not in st.session_state or st.session_state.selected_city != selected_city:
    st.session_state.selected_city = selected_city
    st.session_state.page_refresh = True

logo_html = f"<img src='{logo_src}' style='width:48px;height:48px;object-fit:contain;margin-right:12px;' />" if logo_src else "<div class='title-icon' style='width:48px;height:48px;font-size:1.5rem;background:linear-gradient(135deg,#5EE7FF,#8b5cf6);color:#fff;'>✦</div>"

st.markdown(
    f"""
    <div class='hero-shell' style='display:flex; justify-content:space-between; align-items:center;'>
        <div class='title-row' style='margin-bottom:0;'>
            {logo_html}
            <div>
                <h1 class='page-title' style='font-size:1.8rem; margin:0;'>CivicMind Intelligence</h1>
                <p class='page-subtitle' style='margin:0; font-size:0.95rem;'>Enterprise Decision Platform</p>
            </div>
        </div>
        <div class='hero-meta' style='margin-top:0;'>
            <span class='pill live-pill'><span class='dot'></span> SYSTEM ACTIVE</span>
            <span class='pill'>Updated: {datetime.now().strftime('%H:%M')}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if selected_page == "Analytics":
    render_analytics(selected_city, weather, aqi)
elif selected_page == "City Intelligence":
    render_city_map(selected_city)
elif selected_page == "Forecast":
    render_forecast(selected_city, weather, aqi)
elif selected_page == "AI Assistant":
    render_assistant(selected_city, weather, aqi)
elif selected_page == "Reports":
    render_reports(selected_city, weather, aqi)
elif selected_page == "Settings":
    render_settings()
else:
    render_dashboard(selected_city, weather, aqi)

render_footer()