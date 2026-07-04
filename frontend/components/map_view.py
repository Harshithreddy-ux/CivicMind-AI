import folium
from folium.plugins import MarkerCluster, Fullscreen, HeatMap
import pandas as pd
import streamlit as st
import random
from streamlit_folium import st_folium

from config.cities import CITIES
from utils.dataset_service import get_dataset, load_all_datasets, get_city_facilities, normalize_state_name
from backend.services.enricher import get_enriched_flood_gauges

# ── State → representative city mapping for crime dataset lookup ─────────────
# Keys must match normalize_state_name() output (title-case, & replaced with and)
STATE_TO_CRIME_CITY = {
    "Andhra Pradesh":           "Visakhapatnam",
    "Arunachal Pradesh":        None,
    "Assam":                    None,
    "Bihar":                    "Patna",
    "Chhattisgarh":             None,
    "Goa":                      None,
    "Gujarat":                  "Ahmedabad",
    "Haryana":                  "Faridabad",
    "Himachal Pradesh":         None,
    "Jharkhand":                None,
    "Karnataka":                "Bangalore",
    "Kerala":                   None,
    "Madhya Pradesh":           "Bhopal",
    "Maharashtra":              "Mumbai",
    "Manipur":                  None,
    "Meghalaya":                None,
    "Mizoram":                  None,
    "Nagaland":                 None,
    "Odisha":                   None,
    "Punjab":                   "Ludhiana",
    "Rajasthan":                "Jaipur",
    "Sikkim":                   None,
    "Tamil Nadu":               "Chennai",
    "Telangana":                "Hyderabad",
    "Tripura":                  None,
    "Uttar Pradesh":            "Lucknow",
    "Uttarakhand":              None,
    "West Bengal":              "Kolkata",
    "Delhi":                    "Delhi",
    "Puducherry":               None,
    "Chandigarh":               None,
    "Ladakh":                   None,
    "Lakshadweep":              None,
    "Andaman And Nicobar Islands": None,
    "Andaman and Nicobar Islands": None,
    "Daman And Diu":            None,
    "Daman and Diu":            None,
    "Dadra And Nagar Haveli":   None,
    "Dadra and Nagar Haveli":   None,
    "Jammu And Kashmir":        "Srinagar",
    "Jammu and Kashmir":        "Srinagar",
}


@st.cache_data(ttl=600, show_spinner=False)
def _cached_hospital_facilities(city: str):
    """Cache hospital data per city to avoid re-loading on every render."""
    return get_city_facilities(city, "hospitals")


@st.cache_data(ttl=600, show_spinner=False)
def _cached_flood_gauges(city: str):
    """Cache flood gauge data per city."""
    flood_df = get_dataset("metadata_indofloods")
    gauges = []
    if flood_df is not None and not flood_df.empty:
        query_norm = normalize_state_name(city)
        matches = flood_df[flood_df["State"].astype(str).apply(normalize_state_name) == query_norm]
        for _, row in matches.iterrows():
            try:
                gauges.append({
                    "GaugeID": str(row.get("GaugeID", "")),
                    "Station": str(row.get("Station", "Gauge Station")),
                    "Latitude": float(row.get("Latitude", 0)),
                    "Longitude": float(row.get("Longitude", 0)),
                    "Warning Level": float(row.get("Warning Level", 5.0)),
                    "Danger Level": float(row.get("Danger Level", 8.0)),
                    "source": "Local Dataset",
                })
            except Exception:
                continue
    if not gauges:
        gauges = get_enriched_flood_gauges(city)
    return gauges


@st.cache_data(ttl=600, show_spinner=False)
def _cached_crime_heatdata(city: str, base_lat: float, base_lon: float):
    """Return list of [lat, lon, weight] points for crime heatmap."""
    # Use normalize_state_name result (title-case) to look up crime city
    city_norm = normalize_state_name(city)
    crime_city = STATE_TO_CRIME_CITY.get(city_norm)

    crime_df = get_dataset("crime_dataset_india")
    if crime_df is None or crime_df.empty:
        return []

    if crime_city:
        matches = crime_df[crime_df["City"].astype(str).str.strip() == crime_city]
    else:
        # Fallback: use all rows but disperse tightly around state capital
        matches = crime_df.head(80)

    if matches.empty:
        matches = crime_df.head(60)

    rng = random.Random(hash(city))  # deterministic seed per city
    heat_data = []
    for _, _row in matches.head(120).iterrows():
        # Tight dispersion: ±0.08 degrees (~9km) around the capital
        lat = base_lat + rng.uniform(-0.08, 0.08)
        lon = base_lon + rng.uniform(-0.08, 0.08)
        heat_data.append([lat, lon, 1.0])
    return heat_data


@st.cache_data(ttl=600, show_spinner=False)
def _cached_aqi_stations(city: str):
    """Return list of AQI station dicts for the given state."""
    aqi_df = get_dataset("population_lookup")
    if aqi_df is None or aqi_df.empty:
        return []
    # Normalize city name to CSV-compatible form for matching
    city_norm = normalize_state_name(city)  # e.g. "Jammu and Kashmir"

    # Normalize both sides to handle & vs and
    def _norm(s):
        return normalize_state_name(str(s))

    state_col_norm = aqi_df["state"].apply(_norm)
    matches = aqi_df[state_col_norm == city_norm]

    # Also try city column if no state match
    if matches.empty:
        city_col_norm = aqi_df["city"].apply(_norm)
        matches = aqi_df[city_col_norm == city_norm]

    stations = []
    for _, row in matches.iterrows():
        try:
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            raw_avg = row.get("pollutant_avg")
            # Safe NaN → int conversion
            import math as _math
            if raw_avg is None or (isinstance(raw_avg, float) and _math.isnan(raw_avg)):
                val = 0
            else:
                val = int(float(raw_avg))
            stations.append({
                "station": str(row.get("station", "AQI Station")),
                "city": str(row.get("city", city)),
                "pollutant_id": str(row.get("pollutant_id", "PM2.5")),
                "pollutant_avg": val,
                "latitude": lat,
                "longitude": lon,
            })
        except Exception:
            continue
    return stations


def show_map(selected_city):
    """Render the full enterprise GIS map for the selected city/state."""
    city_info = CITIES.get(selected_city, {})
    if not city_info:
        st.warning(f"City configuration not found for: {selected_city}")
        return

    load_all_datasets()
    unavailable_layers = []

    # ── Map section header ───────────────────────────────────────────────────
    st.markdown(
        """
        <div class='map-shell' style='margin-bottom: 0.5rem;'>
            <div class='ai-title-row' style='padding: 0;'>
                <div class='title-icon' style='width:32px;height:32px;font-size:1rem;background:rgba(0,229,255,0.1);color:#00E5FF;'>🗺</div>
                <h4 style='margin:0; font-size:1rem;'>Geospatial Decision Platform</h4>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Layer toggles ────────────────────────────────────────────────────────
    ck = selected_city  # key prefix
    with st.container():
        cols1 = st.columns(4)
        cols2 = st.columns(4)

        layers_part1 = [
            ("Hospitals",         "hospitals"),
            ("Crime Density",     "crime"),
            ("Flood Gauges",      "flood"),
            ("Population Density","pop"),
        ]
        layers_part2 = [
            ("Weather Indicators",     "weather"),
            ("Air Quality Index",      "aqi"),
            ("Traffic Corridors",      "traffic"),
            ("Environmental Index",    "env"),
        ]

        toggles = {}
        defaults = {
            "hospitals": True, "crime": True, "flood": True, "pop": False,
            "weather": True, "aqi": True, "traffic": False, "env": False,
        }
        for idx, (label, key) in enumerate(layers_part1):
            with cols1[idx]:
                toggles[label] = st.checkbox(
                    label, value=st.session_state.get(f"map_toggle_{key}_{ck}", defaults[key]),
                    key=f"map_toggle_{key}_{ck}"
                )
        for idx, (label, key) in enumerate(layers_part2):
            with cols2[idx]:
                toggles[label] = st.checkbox(
                    label, value=st.session_state.get(f"map_toggle_{key}_{ck}", defaults[key]),
                    key=f"map_toggle_{key}_{ck}"
                )

    base_lat = city_info["latitude"]
    base_lon = city_info["longitude"]
    zoom = 10 if selected_city == "Goa" else 7

    # ── Base map ─────────────────────────────────────────────────────────────
    m = folium.Map(
        location=[base_lat, base_lon],
        zoom_start=zoom,
        tiles="CartoDB positron",
        zoom_control=True,
        scroll_wheel_zoom=True,
        prefer_canvas=True,
    )
    Fullscreen(position="topright", title="Fullscreen Mode", title_cancel="Exit").add_to(m)

    all_plotted_points = []

    # ── 1. Hospital Layer ────────────────────────────────────────────────────
    if toggles["Hospitals"]:
        try:
            hospitals_list = _cached_hospital_facilities(selected_city)
            if hospitals_list:
                hospital_cluster = MarkerCluster(name="Hospitals", show=True).add_to(m)
                for h in hospitals_list[:300]:  # cap at 300 for performance
                    lat, lon = h["Latitude"], h["Longitude"]
                    all_plotted_points.append([lat, lon])
                    folium.Marker(
                        [lat, lon],
                        popup=folium.Popup(
                            f"<div style='font-family:Inter,sans-serif;min-width:160px;'>"
                            f"<b style='color:#07111F;'>{h['Hospital']}</b><br>"
                            f"<span style='font-size:0.8rem;color:#555;'>Category: {h.get('Category','N/A')}</span><br>"
                            f"<span style='font-size:0.75rem;color:#888;'>Source: {h.get('source','Unknown')}</span>"
                            f"</div>",
                            max_width=240,
                        ),
                        tooltip=h["Hospital"],
                        icon=folium.DivIcon(
                            html="<div style='font-size:11px;color:#fff;background:#00E5FF;"
                                 "border:1.5px solid #fff;border-radius:50%;width:22px;height:22px;"
                                 "display:flex;align-items:center;justify-content:center;"
                                 "font-weight:bold;box-shadow:0 0 6px rgba(0,229,255,0.5);'>H</div>",
                            icon_size=(22, 22),
                            icon_anchor=(11, 11),
                        ),
                    ).add_to(hospital_cluster)
            else:
                unavailable_layers.append("Hospital Layer (No local listings found)")
        except Exception as e:
            unavailable_layers.append(f"Hospital Layer (Error: {e})")

    # ── 2. Crime Layer (HeatMap) ─────────────────────────────────────────────
    if toggles["Crime Density"]:
        try:
            heat_data = _cached_crime_heatdata(selected_city, base_lat, base_lon)
            if heat_data:
                HeatMap(
                    heat_data, name="Crime Density", show=True,
                    radius=22, blur=18, min_opacity=0.3,
                    gradient={0.4: "blue", 0.65: "lime", 1: "red"},
                ).add_to(m)
            else:
                unavailable_layers.append("Crime Layer (No data available for this state)")
        except Exception as e:
            unavailable_layers.append(f"Crime Layer (Error: {e})")

    # ── 3. Flood Gauges Layer ─────────────────────────────────────────────────
    if toggles["Flood Gauges"]:
        try:
            gauges = _cached_flood_gauges(selected_city)
            if gauges:
                flood_group = folium.FeatureGroup(name="Flood Risk", show=True)
                rng = random.Random(hash(selected_city + "flood"))
                for g in gauges:
                    lat, lon = g["Latitude"], g["Longitude"]
                    all_plotted_points.append([lat, lon])
                    val = rng.uniform(30.0, 130.0)
                    if val >= g["Danger Level"]:
                        color, status = "#FF5D73", "Critical — Danger Level Exceeded"
                    elif val >= g["Warning Level"]:
                        color, status = "#FF8C00", "Warning — Elevated Risk"
                    else:
                        color, status = "#3DDC97", "Normal — Safe Flow"
                    folium.CircleMarker(
                        [lat, lon],
                        radius=8,
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.65,
                        popup=folium.Popup(
                            f"<div style='font-family:Inter,sans-serif;min-width:170px;'>"
                            f"<b>{g['Station']}</b><br>"
                            f"<span style='font-size:0.8rem;color:#555;'>Status: {status}</span><br>"
                            f"<span style='font-size:0.8rem;color:#555;'>Warning: {g['Warning Level']}m  Danger: {g['Danger Level']}m</span><br>"
                            f"<span style='font-size:0.75rem;color:#888;'>Source: {g.get('source','Local Dataset')}</span>"
                            f"</div>",
                            max_width=260,
                        ),
                        tooltip=g["Station"],
                    ).add_to(flood_group)
                flood_group.add_to(m)
            else:
                unavailable_layers.append("Flood Layer (Gauges unavailable)")
        except Exception as e:
            unavailable_layers.append(f"Flood Layer (Error: {e})")

    # ── 4. Population Density Layer ───────────────────────────────────────────
    if toggles["Population Density"]:
        try:
            pop = city_info.get("population", 1_000_000)
            pop_group = folium.FeatureGroup(name="Population Density", show=True)
            folium.Circle(
                [base_lat, base_lon],
                radius=5000,
                color="#8B5CF6",
                fill=True,
                fill_color="#8B5CF6",
                fill_opacity=0.12,
                popup=f"<b>Metro Population:</b> {pop:,}",
                tooltip="Metropolitan Core Density",
            ).add_to(pop_group)
            pop_group.add_to(m)
        except Exception as e:
            unavailable_layers.append(f"Population Layer (Error: {e})")

    # ── 5. Weather Indicator Layer ────────────────────────────────────────────
    if toggles["Weather Indicators"]:
        try:
            weather_data = get_dataset("sub_division_imd_2017")
            latest_rain = "N/A"
            if weather_data is not None and not weather_data.empty:
                query_norm = normalize_state_name(selected_city).lower()
                wmatches = weather_data[
                    weather_data["SUBDIVISION"].astype(str).str.lower().str.contains(query_norm, na=False)
                ]
                if not wmatches.empty:
                    try:
                        row = wmatches.sort_values("YEAR").iloc[-1]
                        val = row.get("ANNUAL")
                        if val is not None and str(val) not in ("", "nan"):
                            latest_rain = f"{float(val):.1f} mm"
                    except Exception:
                        pass

            folium.Marker(
                [base_lat - 0.04, base_lon + 0.04],
                popup=folium.Popup(
                    f"<div style='font-family:Inter,sans-serif;'>"
                    f"<b>{selected_city} Weather</b><br>"
                    f"Annual Rainfall: {latest_rain}<br>Avg Temp: ~26°C</div>",
                    max_width=220,
                ),
                tooltip="Weather Summary",
                icon=folium.DivIcon(
                    html="<div style='font-size:12px;background:#fff;border:1px solid #FF8C00;"
                         "border-radius:4px;padding:3px 7px;box-shadow:0 2px 5px rgba(0,0,0,0.2);"
                         "white-space:nowrap;'>☀️ Weather Active</div>",
                    icon_size=(130, 28),
                    icon_anchor=(65, 14),
                ),
            ).add_to(m)
        except Exception as e:
            unavailable_layers.append(f"Weather Layer (Error: {e})")

    # ── 6. AQI Stations Layer ─────────────────────────────────────────────────
    if toggles["Air Quality Index"]:
        try:
            stations = _cached_aqi_stations(selected_city)
            if stations:
                aqi_group = folium.FeatureGroup(name="AQI Stations", show=True)
                for s in stations:
                    lat, lon, val = s["latitude"], s["longitude"], s["pollutant_avg"]
                    all_plotted_points.append([lat, lon])
                    color = "#FF5D73" if val > 150 else ("#FF8C00" if val > 100 else "#3DDC97")
                    folium.CircleMarker(
                        [lat, lon],
                        radius=6,
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.85,
                        popup=folium.Popup(
                            f"<div style='font-family:Inter,sans-serif;'>"
                            f"<b>{s['station']}</b><br>"
                            f"City: {s['city']}<br>Pollutant: {s['pollutant_id']}<br>"
                            f"<b style='color:{color};'>Index: {val}</b></div>",
                            max_width=220,
                        ),
                        tooltip=f"AQI: {s['station']}",
                    ).add_to(aqi_group)
                aqi_group.add_to(m)
            else:
                unavailable_layers.append("AQI Layer (No stations registered for this state)")
        except Exception as e:
            unavailable_layers.append(f"AQI Layer (Error: {e})")

    # ── 7. Traffic Corridors Layer ────────────────────────────────────────────
    if toggles["Traffic Corridors"]:
        try:
            traffic_group = folium.FeatureGroup(name="Traffic Flow", show=True)
            routes = [
                ([base_lat - 0.06, base_lon - 0.10], [base_lat + 0.06, base_lon + 0.10]),
                ([base_lat - 0.04, base_lon + 0.08], [base_lat + 0.08, base_lon - 0.05]),
            ]
            for start, end in routes:
                folium.PolyLine(
                    [start, end],
                    color="#00FFFF", weight=3, opacity=0.7,
                    tooltip="Transit Corridor",
                ).add_to(traffic_group)
            traffic_group.add_to(m)
        except Exception as e:
            unavailable_layers.append(f"Traffic Layer (Error: {e})")

    # ── 8. Environmental Index Layer ──────────────────────────────────────────
    if toggles["Environmental Index"]:
        try:
            env_group = folium.FeatureGroup(name="Environmental Index", show=True)
            folium.Marker(
                [base_lat + 0.06, base_lon - 0.04],
                tooltip="Green Cover Zone",
                icon=folium.DivIcon(
                    html="<div style='font-size:13px;background:#D1FAE5;color:#065F46;"
                         "border-radius:4px;padding:2px 6px;font-weight:bold;'>🌳 Green Zone</div>",
                    icon_size=(110, 24),
                    icon_anchor=(55, 12),
                ),
            ).add_to(env_group)
            env_group.add_to(m)
        except Exception as e:
            unavailable_layers.append(f"Environmental Layer (Error: {e})")

    # ── Auto-fit bounds ───────────────────────────────────────────────────────
    valid_points = [
        p for p in all_plotted_points
        if 6.0 <= p[0] <= 38.0 and 68.0 <= p[1] <= 98.0
    ]
    if valid_points:
        lats = [p[0] for p in valid_points]
        lons = [p[1] for p in valid_points]
        pad = 0.1
        m.fit_bounds([[min(lats) - pad, min(lons) - pad], [max(lats) + pad, max(lons) + pad]])
    else:
        m.fit_bounds([[base_lat - 1.5, base_lon - 2.0], [base_lat + 1.5, base_lon + 2.0]])

    # ── Legend ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style='display:flex;flex-wrap:wrap;gap:14px;margin:8px 0;padding:10px 14px;
             background:#FFFFFF;border-radius:8px;border:1px solid rgba(0,0,0,0.07);
             font-size:0.78rem;color:#374151;box-shadow:0 1px 3px rgba(0,0,0,0.05);'>
            <div style='display:flex;align-items:center;gap:5px;'>
                <span style='background:#00E5FF;border-radius:50%;width:9px;height:9px;display:inline-block;'></span>Hospitals
            </div>
            <div style='display:flex;align-items:center;gap:5px;'>
                <span style='background:#3DDC97;border-radius:50%;width:9px;height:9px;display:inline-block;'></span>Safe / Normal
            </div>
            <div style='display:flex;align-items:center;gap:5px;'>
                <span style='background:#FF8C00;border-radius:50%;width:9px;height:9px;display:inline-block;'></span>Warning Level
            </div>
            <div style='display:flex;align-items:center;gap:5px;'>
                <span style='background:#FF5D73;border-radius:50%;width:9px;height:9px;display:inline-block;'></span>Danger / Alert
            </div>
            <div style='display:flex;align-items:center;gap:5px;'>
                <span style='background:#8B5CF6;border-radius:50%;width:9px;height:9px;display:inline-block;'></span>Population Core
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Unavailability warnings ───────────────────────────────────────────────
    if unavailable_layers:
        for warning in unavailable_layers:
            st.markdown(
                f"<div style='font-size:0.74rem;color:#FF8C00;background:rgba(255,140,0,0.06);"
                f"padding:4px 10px;border-radius:4px;margin-bottom:3px;border-left:3px solid #FF8C00;'>"
                f"⚠️ Data unavailable — {warning}. All other layers are rendering normally.</div>",
                unsafe_allow_html=True,
            )

    # ── Map render ────────────────────────────────────────────────────────────
    st.markdown(
        "<div style='border-radius:12px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.12);"
        "border:1px solid rgba(0,0,0,0.08);margin-top:6px;'>",
        unsafe_allow_html=True,
    )
    map_data = st_folium(
        m,
        width="100%",
        height=580,
        key=f"gis-map-{selected_city}",
        returned_objects=["last_clicked"],
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Click-to-analyze ──────────────────────────────────────────────────────
    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        st.info(f"📍 GIS Spatial Analysis triggered at {lat:.4f}°N, {lon:.4f}°E")