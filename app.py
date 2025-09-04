import streamlit as st
import requests
import pandas as pd
from utils.team_generator import generate_teams
from PIL import Image

# Configuratie
st.set_page_config(page_title="Bounceball TEAMS", layout="centered")
logo = Image.open("assets/logo.png")
st.image(logo, width=200)
st.title("Bounceball TEAMS")

# Invoer: spelersnamen en aantal teams
names_input = st.text_area("Voer spelersnamen in (gescheiden door komma's):", height=100)
team_count = st.number_input("Aantal teams:", min_value=2, max_value=10, step=1)

if st.button("Maak teams"):
    if not names_input.strip():
        st.warning("Voer eerst namen in.")
    else:
        spelers_namen = [naam.strip().lower() for naam in names_input.split(",") if naam.strip()]

        # Ophalen van data via jouw Google Script link
        # Spelers ophalen
url_spelers = "https://script.google.com/macros/s/AKfycbwNcRXJjIMIYYcRWKHuIWr_e-KxbzEsC-KrQeU_AFuinZtLKul9JGhpxsImYd_YeLJe/exec"
response_spelers = requests.get(url_spelers)
data_spelers = response_spelers.json()
df_spelers = pd.DataFrame(data_spelers)

# Groepsregels ophalen
url_regels = "https://script.google.com/macros/s/AKfycbwNcRXJjIMIYYcRWKHuIWr_e-KxbzEsC-KrQeU_AFuinZtLKul9JGhpxsImYd_YeLJe/exec?sheet=Groepsregels"
response_regels = requests.get(url_regels)
data_regels = response_regels.json()
df_regels = pd.DataFrame(data_regels)

        # Filter op ingevoerde namen
        df_spelers["naam_lower"] = df_spelers["naam"].str.lower()
        df_spelers = df_spelers[df_spelers["naam_lower"].isin(spelers_namen)].copy()
        df_spelers.drop(columns=["naam_lower"], inplace=True)

        if df_spelers.empty:
            st.error("Geen spelers gevonden met de opgegeven namen.")
        else:
            teams = generate_teams(df_spelers, df_regels, int(team_count))
            for i, team in enumerate(teams):
                st.subheader(f"Team {i+1} (Gem. rating: {team['average_rating']:.2f})")
                for speler in team["players"]:
                    keeper_tag = "🧤" if speler["keeper"] else ""
                    st.write(f"- {speler['naam']} (Rating: {speler['rating']}) {keeper_tag}")
