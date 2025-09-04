
import streamlit as st
import pandas as pd
import requests
from utils.team_generator import generate_teams

st.set_page_config(page_title="Bounceball TEAMS", layout="centered")

st.title("🏐 Bounceball TEAMS")

names_input = st.text_area(
    "Voer spelersnamen in (gescheiden door komma's):",
    placeholder="Bijv. Roy, Dieuwke, Anjo, Linda, Martijn, ...")

team_count = st.number_input("Aantal teams:", min_value=2, max_value=10, value=2, step=1)

if st.button("Maak teams"):
    if not names_input.strip():
        st.error("Voer eerst spelersnamen in.")
    else:
        try:
            # Ingevoerde namen verwerken
            spelers_namen = [naam.strip().lower() for naam in names_input.split(",") if naam.strip()]

            # Data ophalen van Google Apps Script (Spelers)
            url_spelers = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec?sheet=Spelers"
            response_spelers = requests.get(url_spelers)
            data_spelers = response_spelers.json()
            df_spelers = pd.DataFrame(data_spelers)

            # Data ophalen van Google Apps Script (Groepsregels)
            url_regels = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec?sheet=Groepsregels"
            response_regels = requests.get(url_regels)
            data_regels = response_regels.json()
            df_regels = pd.DataFrame(data_regels)

            # Filteren op ingevoerde spelersnamen
            df_spelers["naam_lower"] = df_spelers["naam"].str.lower()
            df_spelers = df_spelers[df_spelers["naam_lower"].isin(spelers_namen)].copy()
            df_spelers.drop(columns=["naam_lower"], inplace=True)

            if df_spelers.empty:
                st.error("Geen spelers gevonden met de opgegeven namen.")
            else:
                teams = generate_teams(df_spelers, df_regels, int(team_count))
                for i, team in enumerate(teams, start=1):
                    st.subheader(f"Team {i}")
                    st.dataframe(team.reset_index(drop=True))

        except Exception as e:
            st.error(f"Er is een fout opgetreden: {e}")
