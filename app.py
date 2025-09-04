import streamlit as st
import pandas as pd
import requests
from team_generator import generate_teams

# URL naar Google Apps Script voor Spelers
URL_SPELERS = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec"

st.set_page_config(page_title="Bounceball TEAMS")
st.title("🏐 Bounceball TEAMS")

names_input = st.text_area("Voer spelersnamen in (gescheiden door komma's):")
team_count = st.number_input("Aantal teams:", min_value=2, max_value=10, step=1, value=2)
clicked = st.button("Maak teams")

if clicked:
    if not names_input.strip():
        st.warning("⚠️ Geen spelersnamen ingevoerd.")
        st.stop()

    opgegeven_namen = [naam.strip().lower() for naam in names_input.split(",") if naam.strip()]

    try:
        response = requests.get(URL_SPELERS)
        spelers_data = response.json()
        df_spelers = pd.DataFrame(spelers_data)
    except Exception as e:
        st.error(f"❌ Fout bij het ophalen van spelersgegevens: {e}")
        st.stop()

    df_spelers["naam_lower"] = df_spelers["naam"].str.lower()
    df_spelers = df_spelers[df_spelers["naam_lower"].isin(opgegeven_namen)].copy()
    df_spelers.drop(columns=["naam_lower"], inplace=True)

    if df_spelers.empty:
        st.error("⚠️ Geen overeenkomende spelers gevonden.")
        st.stop()

    teams = generate_teams(df_spelers, team_count=int(team_count))

    for i, team in enumerate(teams, start=1):
        st.subheader(f"Team {i}")
        st.table(team.reset_index(drop=True))