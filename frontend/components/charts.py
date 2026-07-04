import streamlit as st

try:
    import plotly.graph_objects as go
except Exception:  # pragma: no cover
    go = None


def render_charts(weather, aqi):
    if go is None:
        st.info("Interactive charts are unavailable in the current environment.")
        return

    if weather is None:
        st.markdown(
            """
            <div class='cm-card' style='padding:1.2rem; text-align:center; min-height:120px; 
                 display:flex; flex-direction:column; align-items:center; justify-content:center;'>
                <div style='font-size:1.8rem; margin-bottom:8px;'>📡</div>
                <div style='font-size:0.85rem; color:#A5B6D6; font-weight:600;'>LIVE TELEMETRY</div>
                <div style='font-size:0.8rem; color:#6B7280; margin-top:4px;'>
                    Weather data is loading from backend. Charts will render automatically once available.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    current = weather.get("current", {})
    temp = current.get("temperature_2m", 25.0)
    humidity = current.get("relative_humidity_2m", 60.0)
    aqi_value = 0
    if aqi and aqi.get("current"):
        raw = aqi["current"].get("us_aqi", 0)
        try:
            aqi_value = float(raw) if raw is not None else 0.0
        except Exception:
            aqi_value = 0.0

    hours = ["6h", "12h", "18h", "24h", "30h"]
    t_series = [temp - 2, temp, temp + 2, temp + 1, temp + 3]
    h_series = [humidity - 5, humidity, humidity - 3, humidity + 2, humidity + 1]
    a_series = [aqi_value * 0.6, aqi_value * 0.75, aqi_value, aqi_value * 0.9, aqi_value * 0.85]

    fig = go.Figure()

    # Temperature spline
    fig.add_trace(go.Scatter(
        x=hours, y=t_series,
        mode="lines+markers",
        name="Temp (°C)",
        line=dict(color="#5EE7FF", width=3, shape="spline"),
        marker=dict(size=6, color="#111B2E", line=dict(width=2, color="#5EE7FF")),
        fill="tozeroy",
        fillcolor="rgba(94,231,255,0.08)",
    ))

    # Humidity spline
    fig.add_trace(go.Scatter(
        x=hours, y=h_series,
        mode="lines+markers",
        name="Humidity (%)",
        line=dict(color="#3DDC97", width=3, shape="spline"),
        marker=dict(size=6, color="#111B2E", line=dict(width=2, color="#3DDC97")),
        fill="tozeroy",
        fillcolor="rgba(61,220,151,0.08)",
    ))

    # AQI bar
    fig.add_trace(go.Bar(
        x=hours, y=a_series,
        name="AQI",
        marker=dict(color="#FF5D73", opacity=0.75),
        width=0.3,
    ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=270,
        showlegend=True,
        legend=dict(
            orientation="h",
            x=0, y=1.1,
            font=dict(color="#A5B6D6", size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#A5B6D6")),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            zeroline=False,
            tickfont=dict(color="#A5B6D6"),
        ),
    )

    st.markdown("<div class='cm-card' style='padding:1rem;'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.85rem;color:#A5B6D6;font-weight:600;margin-bottom:8px;'>LIVE TELEMETRY</div>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)
