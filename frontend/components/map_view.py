import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from config.cities import CITIES


def show_map(selected_city):

    city = CITIES[selected_city]

    m = folium.Map(
        location=[
            city["latitude"],
            city["longitude"]
        ],
        zoom_start=11
    )

    folium.Marker(
        [
            city["latitude"],
            city["longitude"]
        ],
        popup=selected_city,
        icon=folium.Icon(
            color="red",
            icon="home"
        )
    ).add_to(m)

    hospitals = pd.read_csv(
        "datasets/hospitals.csv"
    )

    hospitals = hospitals[
        hospitals["City"] == selected_city
    ]

    for _, row in hospitals.iterrows():

        folium.Marker(

            [
                row["Latitude"],
                row["Longitude"]
            ],

            popup=row["Hospital"],

            tooltip=row["Hospital"],

            icon=folium.Icon(
                color="green",
                icon="plus-sign"
            )

        ).add_to(m)

    st.subheader("🗺 Smart City Intelligence Map")

    st_folium(
        m,
        width=900,
        height=500
    )