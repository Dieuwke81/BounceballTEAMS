import streamlit as st
import pandas as pd
import numpy as np
import requests
import random

# --- PAGINA CONFIG & LOGO ---
st.set_page_config(page_title="Bounceball TEAMS", layout="centered")
st.markdown("<div style='text-align: center;'><img src='https://raw.githubusercontent.com/Dieuwke81/BounceballTEAMS/refs/heads/main/logo.png' width='200'></div>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Bounceball<br>TEAMS</h1>", unsafe_allow_html=True)

# --- INPUTVELDEN ---
namen_input = st.text_input("Voer spelersnamen in die meedoen (gescheiden door komma's):")
aantal_teams = st.number_input("Aantal teams:", min_value=2, max_value=10, value=2, step=1)

samen_input = st.text_input("Spelers die samen in een team moeten (bijv: Linda-Pim, Roy-Gijs):")
niet_samen_input = st.text_input("Spelers die niet samen in een team mogen (bijv: Gijs-Lotte):")

maak_teams_button = st.button("Maak teams")

# --- GEGEVENS LADEN ---
@st.cache_data
def haal_spelers_data_op():
    url = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec"
    response = requests.get(url)
    return pd.DataFrame(response.json())

# --- TEAM GENERATOR FUNCTIE ---
def genereer_teams(spelers_df, aantal_teams, samen_duos, niet_samen_duos, simulaties=50000):
    keepers = spelers_df[spelers_df["keeper"] == "ja"].copy()
    veldspelers = spelers_df[spelers_df["keeper"] != "ja"].copy()

    # Verdeelschema bepalen
    total_players = len(spelers_df)
    base_team_size = total_players // aantal_teams
    extra = total_players % aantal_teams
    verdeling = [base_team_size + 1 if i < extra else base_team_size for i in range(aantal_teams)]

    beste_teams = None
    beste_verschil = float("inf")

    for _ in range(simulaties):
        teams = [[] for _ in range(aantal_teams)]

        # Shuffle keepers en verdeel eerlijk
        shuffled_keepers = keepers.sample(frac=1).to_dict(orient="records")
        for i, keeper in enumerate(shuffled_keepers):
            teams[i % aantal_teams].append(keeper)

        # Shuffle overige spelers
        shuffled_spelers = veldspelers.sample(frac=1).to_dict(orient="records")
        team_index = 0
        for speler in shuffled_spelers:
            while len(teams[team_index]) >= verdeling[team_index]:
                team_index = (team_index + 1) % aantal_teams
            teams[team_index].append(speler)

        # Check teamverdeling
        team_lengtes = [len(team) for team in teams]
        if team_lengtes != verdeling:
            continue

        # Check regels
        geldig = True
        for duo in samen_duos:
            in_zelfde_team = any(
                duo[0].lower() in [p["naam"].lower() for p in team] and
                duo[1].lower() in [p["naam"].lower() for p in team]
                for team in teams
            )
            if not in_zelfde_team:
                geldig = False
                break

        for duo in niet_samen_duos:
            in_zelfde_team = any(
                duo[0].lower() in [p["naam"].lower() for p in team] and
                duo[1].lower() in [p["naam"].lower() for p in team]
                for team in teams
            )
            if in_zelfde_team:
                geldig = False
                break

        if not geldig:
            continue

        # Gemiddelde ratings berekenen
        gemiddelden = [np.mean([float(sp["rating"]) for sp in team]) for team in teams]
        verschil = max(gemiddelden) - min(gemiddelden)

        if verschil < beste_verschil:
            beste_verschil = verschil
            beste_teams = teams

    return beste_teams, beste_verschil

# --- PARSEN VAN DUO-INVOER ---
def parse_duos(input_string):
    duos = []
    for item in input_string.split(","):
        item = item.strip()
        if "-" in item:
            parts = item.split("-")
            if len(parts) == 2:
                duos.append((parts[0].strip(), parts[1].strip()))
    return duos[:4]

# --- KNOP INGEDRUKT ---
if maak_teams_button and namen_input:
    ingevoerde_namen = [naam.strip().lower() for naam in namen_input.split(",")]
    spelers_data = haal_spelers_data_op()

    spelers_data["naam_lower"] = spelers_data["naam"].str.lower()
    geselecteerde_spelers = spelers_data[spelers_data["naam_lower"].isin(ingevoerde_namen)].drop(columns=["naam_lower"])

    if len(geselecteerde_spelers) < aantal_teams:
        st.error("Niet genoeg spelers voor het aantal teams.")
    else:
        samen_duos = parse_duos(samen_input)
        niet_samen_duos = parse_duos(niet_samen_input)

        teams, verschil = genereer_teams(geselecteerde_spelers, aantal_teams, samen_duos, niet_samen_duos)

        if teams is None:
            st.error("❌ Geen geldige teamverdeling gevonden met deze voorwaarden.")
        else:
            st.success("✅ Beste teamverdeling gevonden:")
            for i, team in enumerate(teams, 1):
                team_df = pd.DataFrame(team)
                gemiddelde = round(team_df["rating"].astype(float).mean(), 2)
                keepers = team_df[team_df["keeper"] == "ja"]["naam"].tolist()

                st.markdown(f"### Team {i}")
                st.dataframe(team_df[["naam", "rating", "keeper"]], hide_index=True)
                st.markdown(f"**Gemiddelde rating:** {gemiddelde}")
                st.markdown(f"**Keeper(s):** {', '.join(keepers) if keepers else 'Geen'}")

            st.markdown(f"### 📊 Ratingverschil tussen hoogste en laagste team: `{round(verschil, 2)}`")
st.markdown("<p style='text-align: right; font-size: 10px; color: gray;'>Made by Dieuwke</p>", unsafe_allow_html=True)
