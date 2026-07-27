import streamlit as st


def calculate_score(weather, aqi):
    score = 100

    if weather and isinstance(weather, dict) and "current" in weather:
        current = weather["current"]
        if isinstance(current, dict):
            temp = current.get("temperature_2m", 25.0)
            humidity = current.get("relative_humidity_2m", 60.0)
            wind = current.get("wind_speed_10m", 10.0)

            if temp > 40:
                score -= 15
            if humidity > 85:
                score -= 10
            if wind > 35:
                score -= 10

    if aqi and isinstance(aqi, dict) and "current" in aqi:
        try:
            current_aqi = aqi["current"]
            if isinstance(current_aqi, dict):
                aqi_value = current_aqi.get("us_aqi")
                if aqi_value is not None:
                    if aqi_value > 150:
                        score -= 40
                    elif aqi_value > 100:
                        score -= 20
                    elif aqi_value > 50:
                        score -= 10
        except Exception:
            pass

    return max(score, 0)


def show_risk_score(weather, aqi):
    score = calculate_score(weather, aqi)
    degree = int(score * 3.6)
    color = "#35d399"
    status = "Excellent"
    if score < 85:
        color = "#fbbf24"
        status = "Moderate"
    if score < 65:
        color = "#fb7185"
        status = "Critical"

    st.markdown(
        f"""
        <div class='health-card'>
            <div class='gauge-wrap'>
                <div class='gauge' style='background: conic-gradient({color} 0deg, {color} {degree}deg, rgba(255,255,255,0.06) {degree}deg);'>
                    <div class='gauge-inner'>
                        <div class='gauge-score'>{score}%</div>
                        <div class='gauge-label'>{status}</div>
                    </div>
                </div>
            </div>
            <div class='health-copy'>
                <h4>City Health Score</h4>
                <p>Urban resilience is {status.lower()} with a live readiness index of {score}%.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )