import streamlit as st
import requests
from components.cards import BACKEND

def get_recommendation(city):

    try:

        response = requests.get(
            f"{BACKEND}/recommendation?city={city}",
            timeout=5
        )

        if response.status_code == 200:
            return response.json()

    except Exception:
        pass

    return None


def recommendation_panel(city):

    data = get_recommendation(city)

    st.subheader("🧠 AI Decision Assistant")

    if not data:

        st.error("Unable to generate recommendations.")

        return

    risk = data["risk"]

    if risk == "High":
        st.error(f"🚨 Risk Level : {risk}")

    elif risk == "Medium":
        st.warning(f"⚠️ Risk Level : {risk}")

    else:
        st.success(f"✅ Risk Level : {risk}")

    st.markdown("### Recommended Actions")

    for item in data["recommendation"]:
        st.write(f"• {item}")

    st.caption(f"Confidence : {data['confidence']}")