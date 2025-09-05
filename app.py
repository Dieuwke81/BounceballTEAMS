
import streamlit as st
import pandas as pd
import random
import requests
import urllib.parse

# --- SETTINGS ---
API_URL = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec"
LOGO_URL = "https://raw.githubusercontent.com/Dieuwke81/BounceballTEAMS/main/logo.png"
ITERATIONS = 50000

# --- HELPER FUNCTIES ---
def fetch_spelers():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception as e:
        st.error("Fout bij ophalen van spelersgegevens.")
        st.stop()

def valideer_duo_input(input_string, alle_namen):
    if not input_string.strip():
        return []
    duo_paren = []
    regels = input_string.strip().split("\n")
    for regel in regels:
        if "-" not in regel:
            st.error(f"Verkeerde notatie: '{regel}' (gebruik 'Naam1 - Naam2')")
            st.stop()
        naam1, naam2 = [n.strip() for n in regel.split("-")]
        if naam1 not in alle_namen or naam2 not in alle_namen:
            st.error(f"Spelers '{naam1}' of '{naam2}' niet gevonden in lijst.")
            st.stop()
        duo_paren.append((naam1, naam2))
    return duo_paren

def spelers_in_duo(speler, duo_lijst):
    return any(speler in duo for duo in duo_lijst)

def zijn_in_zelfde_team(team, duo):
    return duo[0] in team and duo[1] in team

def zijn_in_verschillende_teams(teams, duo):
    return any(duo[0] in t and duo[1] not in t for t in teams)

def verdeel_teams(spelers, aantal_teams, samen_duos, niet_samen_duos):
    beste_teams = None
    beste_verschil = float("inf")

    keepers = [s for s in spelers if s["keeper"]]
    anderen = [s for s in spelers if not s["keeper"]]

    team_grootte = len(spelers) // aantal_teams
    rest = len(spelers) % aantal_teams

    for _ in range(ITERATIONS):
        random.shuffle(keepers)
        random.shuffle(anderen)

        teams = [[] for _ in range(aantal_teams)]

        # Verdeel keepers
        for i, keeper in enumerate(keepers):
            teams[i % aantal_teams].append(keeper)

        # Verdeel overige spelers
        overige_spelers = anderen.copy()
        for speler in overige_spelers:
            # Stop in team met minste spelers
            kleinste_teams = sorted(teams, key=lambda t: len(t))
            for team in kleinste_teams:
                team.append(speler)
                break

        # Controleer duo's
        if any(not zijn_in_zelfde_team(team, duo) for duo in samen_duos for team in teams):
            continue
        if any(zijn_in_verschillende_teams(teams, duo) for duo in niet_samen_duos):
            continue

        # Bereken ratingverschil
        gemiddelden = [sum(s["rating"] for s in t) / len(t) for t in teams]
        verschil = max(gemiddelden) - min(gemiddelden)

        # Sla beste op
        if verschil < beste_verschil:
            beste_teams = [t.copy() for t in teams]
            beste_verschil = verschil
            if verschil == 0:
                break

    return beste_teams, beste_verschil

# --- STREAMLIT UI ---
st.markdown(f"<div style='text-align: center;'><img src='{LOGO_URL}' width='200'></div>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Bounceball<br>TEAMS</h1>", unsafe_allow_html=True)

namen_input = st.text_input("Voer spelersnamen in die meedoen (gescheiden door komma's):")
aantal_teams = st.number_input("Aantal teams:", min_value=2, max_value=10, value=2, step=1)
samen_input = st.text_area("Spelers die samen in 1 team moeten (één duo per regel, bv: Linda - Roy):", height=100)
niet_samen_input = st.text_area("Spelers die NIET samen in 1 team mogen (zelfde notatie):", height=100)

if st.button("Maak teams") and namen_input.strip():
    ingevoerde_namen = [naam.strip().capitalize() for naam in namen_input.split(",") if naam.strip()]
    spelers_df = fetch_spelers()
    spelers_data = spelers_df[spelers_df["naam"].str.capitalize().isin(ingevoerde_namen)]

    if spelers_data.empty:
        st.error("Geen spelers gevonden met deze namen.")
        st.stop()

    alle_namen = spelers_data["naam"].str.capitalize().tolist()
    samen_duos = valideer_duo_input(samen_input, alle_namen)
    niet_samen_duos = valideer_duo_input(niet_samen_input, alle_namen)

    spelers_dict = spelers_data.to_dict(orient="records")
    teams, verschil = verdeel_teams(spelers_dict, aantal_teams, samen_duos, niet_samen_duos)

    if not teams:
        st.error("Geen geldige teamverdeling gevonden na veel pogingen. Pas je input aan.")
        st.stop()

    st.success("Teams succesvol gegenereerd!")
    for i, team in enumerate(teams, 1):
        rating = sum(p["rating"] for p in team) / len(team)
        st.markdown(f"### Team {i} (gemiddelde rating: {rating:.2f})")
        df_team = pd.DataFrame(team)
        df_team["keeper"] = df_team["keeper"].apply(lambda x: "ja" if x else "nee")
        st.dataframe(df_team[["naam", "rating", "keeper"]], use_container_width=True)
