
import streamlit as st
import pandas as pd
import requests
from team_generator import generate_teams

# URLs naar Google Apps Script
URL_SPELERS = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec?sheet=Spelers"
URL_REGELS = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec?sheet=Groepsregels"

st.title("Bounceball TEAMS")

names_input = st.text_area("Voer spelersnamen in (gescheiden door komma's):")
team_count = st.number_input("Aantal teams:", min_value=2, step=1, value=2)
start = st.button("Maak teams")

if start:
    try:
        # Spelers ophalen
        response_spelers = requests.get(URL_SPELERS)
        data_spelers = response_spelers.json()
        df_spelers = pd.DataFrame(data_spelers)

        # Groepsregels ophalen
        response_regels = requests.get(URL_REGELS)
        data_regels = response_regels.json()
        df_regels = pd.DataFrame(data_regels)

        # Ingevoerde namen verwerken
        spelers_namen = [naam.strip().lower() for naam in names_input.split(",") if naam.strip()]

        # Spelers filteren op invoer
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

    except requests.exceptions.RequestException as e:
        st.error(f"Fout bij ophalen van data: {e}")
    except ValueError as e:
        st.error(f"Ongeldige JSON ontvangen: {e}")
    except Exception as e:
        st.error(f"Er is een fout opgetreden: {e}")
