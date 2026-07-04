import streamlit as st
import pandas as pd
from datetime import datetime
from utils.dataset_service import get_city_facilities, get_city_population, get_city_rainfall

def render_reports(selected_city, weather, aqi):
    st.markdown("## Reports & Exports")
    st.caption("Generate and download export-ready municipal reports and daily operational summaries.")

    population = get_city_population(selected_city)
    rainfall = get_city_rainfall(selected_city)
    hospitals = get_city_facilities(selected_city, "hospitals")

    # Safely extract weather and AQI values
    temp_val = "N/A"
    humidity_val = "N/A"
    if weather and isinstance(weather, dict):
        current_weather = weather.get("current")
        if isinstance(current_weather, dict):
            temp_val = current_weather.get("temperature_2m", "N/A")
            humidity_val = current_weather.get("relative_humidity_2m", "N/A")

    aqi_val = "N/A"
    if aqi and isinstance(aqi, dict):
        current_aqi = aqi.get("current")
        if isinstance(current_aqi, dict):
            aqi_val = current_aqi.get("us_aqi", "N/A")

    # Pre-format population and rainfall safely to avoid format specifier errors
    try:
        pop_str = f"{int(population):,}" if population is not None else "N/A"
    except (ValueError, TypeError):
        pop_str = "N/A"

    try:
        rain_str = f"{float(rainfall):.1f}" if rainfall is not None else "N/A"
    except (ValueError, TypeError):
        rain_str = "N/A"

    # Create formatted Markdown report
    markdown_report = f"""# CivicMind AI - Executive Operational Report
**City/State:** {selected_city}
**Date Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
--------------------------------------------------

## 1. Demographic & Environmental Summary
- **Population:** {pop_str}
- **Annual Average Rainfall:** {rain_str} mm
- **Healthcare Facilities (Hospitals):** {len(hospitals)}

## 2. Weather & Air Quality Status
- **Current Temperature:** {temp_val} °C
- **Relative Humidity:** {humidity_val}%
- **US AQI Value:** {aqi_val}

## 3. Operational Risk Summary
- **Calculated Risk Index:** Moderate
- **Primary Hazards:** Air exposure, thermal context

## 4. Recommended Actions
1. Monitor regional AQI changes.
2. Ensure hospital networks are updated with recent telemetry.
3. Coordinate with emergency services in high-risk zones.
"""

    # Create formatted CSV summary
    csv_df = pd.DataFrame([
        {"Metric": "City", "Value": selected_city},
        {"Metric": "Population", "Value": population},
        {"Metric": "Rainfall (mm)", "Value": rainfall},
        {"Metric": "Hospitals", "Value": len(hospitals)},
        {"Metric": "Temperature (°C)", "Value": temp_val},
        {"Metric": "AQI", "Value": aqi_val},
    ])
    csv_data = csv_df.to_csv(index=False)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='cm-card' style='padding: 1.2rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        st.markdown("### Executive Report")
        st.caption("Comprehensive analysis containing telemetry, demographic statistics, and action plans.")
        st.download_button(
            label="📄 Download Executive Report (.md)",
            data=markdown_report,
            file_name=f"civicmind_report_{selected_city.lower().replace(' ', '_')}.md",
            mime="text/markdown",
            key="btn_download_report"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='cm-card' style='padding: 1.2rem;'>", unsafe_allow_html=True)
        st.markdown("### Emergency Response Report")
        st.caption("Standard operational plan for medical and environmental relief coordination.")
        st.download_button(
            label="🚨 Download Emergency Report (.md)",
            data=f"# CivicMind AI - Emergency Coordination Plan\nCity: {selected_city}\nDate: {datetime.now().strftime('%Y-%m-%d')}\n\n1. Alert emergency networks.\n2. Dispatch medical reserves near local hospital hubs ({len(hospitals)} active).",
            file_name=f"civicmind_emergency_{selected_city.lower().replace(' ', '_')}.md",
            mime="text/markdown",
            key="btn_download_emergency"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='cm-card' style='padding: 1.2rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        st.markdown("### Data Summary (CSV)")
        st.caption("Raw municipal metric exports suitable for third-party spreadsheet ingestion.")
        st.download_button(
            label="📊 Download CSV Summary",
            data=csv_data,
            file_name=f"civicmind_summary_{selected_city.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            key="btn_download_csv"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='cm-card' style='padding: 1.2rem;'>", unsafe_allow_html=True)
        st.markdown("### Daily Summary Export")
        st.caption("Standard JSON dump containing operational telemetry values.")
        import json
        json_data = json.dumps({
            "city": selected_city,
            "timestamp": datetime.now().isoformat(),
            "population": population,
            "rainfall_mm": rainfall,
            "active_hospitals": len(hospitals),
            "weather": weather.get("current", {}) if weather else {},
            "aqi": aqi.get("current", {}) if aqi else {},
        }, indent=2)
        st.download_button(
            label="💾 Download JSON Export",
            data=json_data,
            file_name=f"civicmind_export_{selected_city.lower().replace(' ', '_')}.json",
            mime="application/json",
            key="btn_download_json"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Live Operational Summary")
    st.write({
        "city": selected_city,
        "population": population,
        "rainfall_avg_mm": rainfall,
        "hospitals_count": len(hospitals),
        "status": "Ready for export",
    })
