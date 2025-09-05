
import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
import random
import re
from itertools import combinations

st.set_page_config(page_title="Bounceball TEAMS", layout="centered")

# --- Logo in het midden ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("https://raw.githubusercontent.com/Dieuwke81/BounceballTEAMS/refs/heads/main/logo.png", use_column_width=True)

st.markdown("<h1 style='text-align: center;'>Bounceball<br>TEAMS</h1>", unsafe_allow_html=True)

# --- Invoer spelers ---
spelers_input = st.text_area("Voer spelersnamen in die meedoen (één per regel, nummering mag):")

# Verwerk invoer: verwijder nummering en lege regels
spelers = []
for line in spelers_input.split("\n"):
    line = re.sub(r"^\s*\d+\.?\s*", "", line).strip()
    if line:
        spelers.append(line)

# Aantal teams
aantal_teams = st.number_input("Aantal teams:", min_value=2, max_value=10, value=2, step=1)

# Duo’s die samen moeten
duo_moet_input = st.text_input("Spelers die samen in een team moeten (bijv: Linda-Roy, Gijs-Daan):")
duo_moet = [tuple(map(str.strip, x.split("-"))) for x in duo_moet_input.split(",") if "-" in x]

# Duo’s die niet samen mogen
duo_mag_niet_input = st.text_input("Spelers die niet samen in een team mogen (bijv: Gijs-Lotte):")
duo_mag_niet = [tuple(map(str.strip, x.split("-"))) for x in duo_mag_niet_input.split(",") if "-" in x]

# Dummy ratings ophalen uit Google Sheets API
@st.cache_data
def haal_rating_data():
    url = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec"
    df = pd.read_json(url)
    return df

# Teamverdeling met optimalisatie
def verdeel_teams(spelerslijst, ratings_df, n_teams, verplicht_samen, verboden_samen):
    best_teams = None
    kleinste_verschil = float("inf")
    iterations = 50000

    for _ in range(iterations):
        random.shuffle(spelerslijst)

        # Basisverdeling
        team_sizes = [len(spelerslijst) // n_teams] * n_teams
        for i in range(len(spelerslijst) % n_teams):
            team_sizes[i] += 1

        teams = []
        start = 0
        for size in team_sizes:
            teams.append(spelerslijst[start:start + size])
            start += size

        # Check verplicht samen
        if any(not any(a in t and b in t for t in teams) for a, b in verplicht_samen):
            continue

        # Check verboden samen
        if any(any(a in t and b in t for t in teams) for a, b in verboden_samen):
            continue

        try:
            team_ratings = [np.mean([ratings_df.loc[ratings_df['naam'].str.lower() == s.lower(), 'rating'].values[0] for s in t]) for t in teams]
        except IndexError:
            continue  # speler niet gevonden in ratings

        verschil = max(team_ratings) - min(team_ratings)

        if verschil < kleinste_verschil:
            kleinste_verschil = verschil
            best_teams = (teams, team_ratings)

            if verschil == 0:
                break

    return best_teams if best_teams else ([], [])

# --- Verwerking ---
if st.button("Maak teams"):
    if len(spelers) < aantal_teams:
        st.error("Niet genoeg spelers voor het aantal teams.")
    else:
        ratings = haal_rating_data()
        teams, gemiddelden = verdeel_teams(spelers, ratings, aantal_teams, duo_moet, duo_mag_niet)

        if not teams:
            st.error("Er kon geen geldige teamverdeling worden gemaakt.")
        else:
            for i, (team, avg) in enumerate(zip(teams, gemiddelden), 1):
                st.subheader(f"Team {i} (gem. rating: {avg:.2f})")
                for speler in team:
                    st.write(f"- {speler}")
