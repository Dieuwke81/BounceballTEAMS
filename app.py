import streamlit as st
import pandas as pd
import requests
from team_generator import generate_teams

# Titel en invoer
st.title("Bounceball TEAMS")
names_input = st.text_area("Voer spelersnamen in (gescheiden door komma's):")
team_count = st.number_input("Aantal teams:", min_value=2, max_value=10, value=2, step=1)
submit = st.button("Maak teams")

# URLs naar Google Sheets via Apps Script
spelers_url = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec?sheet=Spelers"
regels_url = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec?sheet=Groepsregels"

if submit:
    try:
        response_spelers = requests.get(spelers_url)
        response_spelers.raise_for_status()
        data_spelers = response_spelers.json()

        response_regels = requests.get(regels_url)
        response_regels.raise_for_status()
        data_regels = response_regels.json()

        df_spelers = pd.DataFrame(data_spelers)
        df_regels = pd.DataFrame(data_regels)

        # Namen filteren
        spelers_namen = [naam.strip().lower() for naam in names_input.split(",") if naam.strip()]
        df_spelers["naam_lower"] = df_spelers["naam"].str.lower()
        df_spelers = df_spelers[df_spelers["naam_lower"].isin(spelers_namen)].copy()
        df_spelers.drop(columns=["naam_lower"], inplace=True)

        if df_spelers.empty:
            st.error("Geen spelers gevonden met de opgegeven namen.")
        else:
            teams = generate_teams(df_spelers, df_regels, int(team_count))
            for i, team in enumerate(teams, start=1):
                st.subheader(f"Team {i}")
                st.table(team)

    except Exception as e:
        st.error(f"Fout: {e}")