import streamlit as st
from datetime import datetime

from utils.dataset_service import get_city_population


@st.cache_data(ttl=600, show_spinner=False)
def _get_hospital_count(city: str) -> int:
    """Cache hospital count per city – avoids re-reading the 30k-row CSV on every render."""
    from utils.dataset_service import get_city_facilities
    return len(get_city_facilities(city, "hospitals"))


def city_status(*args, **kwargs):
    city = kwargs.get("city")
    if city is None and args:
        city = args[0]

    weather = kwargs.get("weather")
    if weather is None and len(args) > 1:
        weather = args[1]

    aqi = kwargs.get("aqi")
    if aqi is None and len(args) > 2:
        aqi = args[2]

    st.markdown(
        "<div class='ai-title-row'><div class='title-icon' style='width:38px;height:38px;font-size:1rem;'>🌍</div>"
        "<h4 style='margin:0;'>City Status</h4></div>",
        unsafe_allow_html=True,
    )

    current = weather.get("current") if weather else None
    aqi_value = "--"
    if aqi and aqi.get("current"):
        try:
            aqi_value = aqi["current"].get("us_aqi", "--")
        except Exception:
            pass

    population = get_city_population(city) if city else None
    hospital_count = _get_hospital_count(city) if city else 0

    stats = [
        ("Temperature", f"{current['temperature_2m']}°C" if current else "—", "Live Weather", "🌡"),
        ("Humidity", f"{current['relative_humidity_2m']}%" if current else "—", "Atmospheric", "💧"),
        ("Wind Speed", f"{current['wind_speed_10m']} km/h" if current else "—", "Surface Flow", "💨"),
        ("Air Quality", str(aqi_value), "AQI Index", "🌫"),
        ("Population", f"{population:,}" if population else "—", "Registered", "👥"),
        ("Hospitals", str(hospital_count), "Facilities", "🏥"),
    ]

    cols = st.columns(3)
    for idx, (label, value, detail, icon) in enumerate(stats):
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class='status-tile'>
                    <div class='status-icon'>{icon}</div>
                    <div class='tile-content'>
                        <strong>{label}</strong>
                        <span>{value}</span>
                        <small style='color:#6B7280;font-size:0.72rem;'>{detail}</small>
                    </div>
                    <div class='status-indicator'></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.caption(
        f"Last updated {datetime.now().strftime('%H:%M:%S')} · Cached telemetry used where live data is pending."
    )