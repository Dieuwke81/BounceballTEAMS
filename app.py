import streamlit as st
import pandas as pd
import requests
import json
from team_generator import generate_teams
from PIL import Image

st.set_page_config(page_title="Bounceball TEAMS", layout="centered")

# Logo en titel
col1, col2 = st.columns([1, 6])
with col1:
    st.image("logo.png", width=80)
with col2:
    st.title("Bounceball TEAMS")

# Inputvelden
names_input = st.text_area("Voer spelersnamen in (gescheiden door komma's):")
team_count = st.number_input("Aantal teams:", min_value=2, max_value=10, value=2, step=1)
button = st.button("Maak teams")

if button:
    spelers_namen = [naam.strip().lower() for naam in names_input.split(",") if naam.strip()]

    if not spelers_namen:
        st.error("Geen geldige namen opgegeven.")
        st.stop()

    # Ophalen van spelersdata
    url_spelers = "https://script.google.com/macros/s/AKfycbwNcRXJjIMIYYcRWKHuIWr_e-KxbzEsC-KrQeU_AFuinZtLKul9JGhpxsImYd_YeLJe/exec"
    response_spelers = requests.get(url_spelers)

    if response_spelers.status_code != 200:
        st.error("Kon spelersgegevens niet ophalen (statuscode niet 200).")
        st.stop()

    try:
        data_spelers = response_spelers.json()
    except json.JSONDecodeError:
        st.error("De spelersdata bevat geen geldige JSON. Controleer je Google Script uitvoer.")
        st.text(response_spelers.text)
        st.stop()

    df_spelers = pd.DataFrame(data_spelers)

    # Ophalen van groepsregels
    url_regels = url_spelers + "?sheet=Groepsregels"
    response_regels = requests.get(url_regels)

    if response_regels.status_code != 200:
        st.error("Kon groepsregels niet ophalen (statuscode niet 200).")
        st.stop()

    try:
        data_regels = response_regels.json()
    except json.JSONDecodeError:
        st.error("De groepsregels bevatten geen geldige JSON. Controleer je Google Sheet.")
        st.text(response_regels.text)
        st.stop()

    df_regels = pd.DataFrame(data_regels)

    # Filter spelers op ingevoerde namen
    df_spelers["naam_lower"] = df_spelers["naam"].str.lower()
    df_spelers = df_spelers[df_spelers["naam_lower"].isin(spelers_namen)].copy()
    df_spelers.drop(columns=["naam_lower"], inplace=True)

    if df_spelers.empty:
        st.error("Geen spelers gevonden met de opgegeven namen.")
    else:
        teams = generate_teams(df_spelers, df_regels, int(team_count))

        for i, team in enumerate(teams, 1):
            st.subheader(f"Team {i} (gemiddelde rating: {team['average_rating']:.2f})")
            for speler in team["players"]:
                keeper_str = " (keeper)" if speler["keeper"] else ""
                st.write(f"- {speler['naam']} (rating: {speler['rating']}){keeper_str}")
