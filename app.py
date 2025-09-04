import streamlit as st
import pandas as pd
import requests
import random

# -------------------
# Instellingen
# -------------------
DATA_URL = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec"

# -------------------
# Functies
# -------------------
def haal_spelers_op():
    try:
        response = requests.get(DATA_URL)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Fout bij ophalen van data: {e}")
        return pd.DataFrame()

def genereer_teams(spelers_df, aantal_teams):
    spelers_df = spelers_df.sample(frac=1).reset_index(drop=True)  # shuffle
    teams = [[] for _ in range(aantal_teams)]

    for idx, speler in spelers_df.iterrows():
        teams[idx % aantal_teams].append(speler["naam"])
    
    return teams

# -------------------
# UI
# -------------------
st.title("Bounceball TEAMS")

names_input = st.text_area("Voer spelersnamen in (gescheiden door komma's):", "")
team_count = st.number_input("Aantal teams:", min_value=2, max_value=10, value=2, step=1)

if st.button("Maak teams"):
    spelers = haal_spelers_op()

    if spelers.empty:
        st.warning("Geen spelersdata beschikbaar. Controleer je Google Script.")
    else:
        # Maak ingevoerde namen lower case & trimmen
        ingevoerd = [naam.strip().lower() for naam in names_input.split(",") if naam.strip()]

        # Kolom toevoegen om te filteren
        spelers["naam_lower"] = spelers["naam"].str.lower()
        geselecteerd = spelers[spelers["naam_lower"].isin(ingevoerd)].copy()

        if geselecteerd.empty:
            st.error("Geen van de ingevoerde namen komt overeen met de database.")
        else:
            teams = genereer_teams(geselecteerd, team_count)
            for i, team in enumerate(teams, 1):
                st.subheader(f"Team {i}")
                st.write(", ".join(team))
