
import streamlit as st
import random
import itertools
import re
import urllib.parse
import pandas as pd
import requests

# Titel en logo
st.markdown("<h1 style='text-align: center;'>Bounceball<br>TEAMS</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center;'><img src='https://raw.githubusercontent.com/Dieuwke81/BounceballTEAMS/main/logo.png' width='150'></div>", unsafe_allow_html=True)
st.write("")

# Speler input
spelers_input = st.text_area("Voer spelersnamen in die meedoen (één per regel, nummering mag):")
aantal_teams = st.number_input("Aantal teams:", min_value=2, max_value=12, value=2, step=1)
samen_input = st.text_input("Spelers die samen in een team moeten (bijv: Linda-Roy, Gijs-Daan):")
niet_samen_input = st.text_input("Spelers die niet samen in een team mogen (bijv: Gijs-Lotte):")

def verwerk_spelers(spelers_input):
    spelers = []
    for regel in spelers_input.strip().split("\n"):
        naam = re.sub(r"^\d+\.?\s*", "", regel.strip())  # Verwijder nummering
        if naam:
            spelers.append(naam)
    return spelers

def parse_constraints(input_text):
    if not input_text.strip():
        return []
    paren = []
    for pair in input_text.split(","):
        namen = [naam.strip() for naam in pair.strip().split("-")]
        if len(namen) == 2:
            paren.append(tuple(namen))
    return paren

def verdeel_teams(spelers, ratings_df, n_teams, verplicht_samen=None, verboden_samen=None, pogingen=5000):
    verplicht_samen = verplicht_samen or []
    verboden_samen = verboden_samen or []

    beste_teams = None
    beste_verschil = float('inf')

    for _ in range(pogingen):
        random.shuffle(spelers)

        teams = [[] for _ in range(n_teams)]
        for i, speler in enumerate(spelers):
            teams[i % n_teams].append(speler)

        # Controleer constraints
        geldig = True
        for a, b in verplicht_samen:
            if not any(a in team and b in team for team in teams):
                geldig = False
                break
        for a, b in verboden_samen:
            if any(a in team and b in team for team in teams):
                geldig = False
                break
        if not geldig:
            continue

        gemiddelden = []
        for team in teams:
            rating = sum(haal_rating(speler, ratings_df) for speler in team)
            gemiddelden.append(rating / len(team))

        verschil = max(gemiddelden) - min(gemiddelden)
        if verschil < beste_verschil:
            beste_verschil = verschil
            beste_teams = teams

    return beste_teams, beste_verschil

# Dummy ratings uit Google Sheets API
def haal_rating_data():
    url = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec"
    try:
        df = pd.read_json(url)
        df["keeper"] = df["keeper"].str.strip().str.lower()  # <-- fix hier
        return df
    except:
        return pd.DataFrame()

def haal_rating(naam, ratings_df):
    try:
        rating = ratings_df.loc[ratings_df["naam"].str.lower() == naam.lower(), "rating"].values[0]
        return float(str(rating).replace(",", "."))
    except:
        return 5.0  # standaard rating

if st.button("Maak teams"):
    spelers = verwerk_spelers(spelers_input)
    verplicht_samen = parse_constraints(samen_input)
    verboden_samen = parse_constraints(niet_samen_input)

    if len(spelers) < aantal_teams:
        st.error("Niet genoeg spelers voor het aantal teams.")
    else:
        ratings = haal_rating_data()
        teams, verschil = verdeel_teams(spelers, ratings, aantal_teams, verplicht_samen, verboden_samen)

        if teams:
            for i, team in enumerate(teams, start=1):
                gemiddelde = sum(haal_rating(speler, ratings) for speler in team) / len(team)
                is_keeper = lambda naam: ratings.loc[ratings["naam"].str.lower() == naam.lower(), "keeper"].values[0] == "ja"
                st.markdown(f"### Team {i} (gem. rating: {gemiddelde:.2f})")
                for speler in team:
                    label = " (keeper)" if is_keeper(speler) else ""
                    st.write(f"- {speler}{label}")
        else:
            st.error("Er kon geen geldige teamverdeling worden gemaakt.")
