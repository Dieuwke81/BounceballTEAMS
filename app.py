import streamlit as st
import pandas as pd
import requests
import random
import copy

# URL naar jouw Google Apps Script
DATA_URL = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec"

st.set_page_config(page_title="Bounceball TEAMS", layout="centered")
st.title("🏐 Bounceball TEAMS")

names_input = st.text_area("Voer spelersnamen in die meedoen (gescheiden door komma's):", "")
num_teams = st.number_input("Aantal teams:", min_value=2, max_value=10, value=2, step=1)

if st.button("Maak teams"):
    if not names_input.strip():
        st.warning("⚠️ Geen namen ingevoerd.")
        st.stop()

    namen = [n.strip().lower() for n in names_input.split(",") if n.strip()]

    try:
        response = requests.get(DATA_URL)
        spelers_data = response.json()
        df = pd.DataFrame(spelers_data)
    except Exception as e:
        st.error(f"Fout bij ophalen van data: {e}")
        st.stop()

    # Filter op ingevoerde namen
    df["naam_lower"] = df["naam"].str.lower()
    df = df[df["naam_lower"].isin(namen)].copy()
    df.drop(columns=["naam_lower"], inplace=True)

    if df.empty:
        st.error("Geen overeenkomende spelers gevonden.")
        st.stop()

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)

    # Keepers en veldspelers scheiden
    keepers = df[df["keeper"] == "ja"].sort_values(by="rating", ascending=False).reset_index(drop=True)
    veldspelers = df[df["keeper"] != "ja"].reset_index(drop=True)

    # Bereken het beste teamresultaat op basis van Monte Carlo simulatie
    best_teams = None
    best_diff = float("inf")

    for _ in range(5000):
        temp_teams = [[] for _ in range(num_teams)]
        team_ratings = [0.0] * num_teams

        # Verdeel keepers evenredig
        for i, keeper in keepers.iterrows():
            idx = i % num_teams
            temp_teams[idx].append(keeper)
            team_ratings[idx] += keeper["rating"]

        # Shuffle veldspelers
        shuffled = veldspelers.sample(frac=1).reset_index(drop=True)

        # Verdeel random veldspelers
        for i, (_, speler) in enumerate(shuffled.iterrows()):
            idx = i % num_teams
            temp_teams[idx].append(speler)
            team_ratings[idx] += speler["rating"]

        # Bereken verschil tussen hoogste en laagste gemiddelde
        team_sizes = [len(team) for team in temp_teams]
        team_avgs = [team_ratings[i]/team_sizes[i] if team_sizes[i] > 0 else 0 for i in range(num_teams)]
        diff = max(team_avgs) - min(team_avgs)

        if diff < best_diff:
            best_diff = diff
            best_teams = copy.deepcopy(temp_teams)

    # Toon de beste teams
    st.subheader("📋 Beste teamverdeling gevonden")
    for i, team in enumerate(best_teams):
        df_team = pd.DataFrame(team)
        avg_rating = round(df_team["rating"].mean(), 2)
        keepers_in_team = df_team[df_team["keeper"] == "ja"]["naam"].tolist()

        st.markdown(f"### 🟢 Team {i + 1} (Gem. rating: {avg_rating})")
        st.dataframe(df_team[["naam", "rating", "keeper"]].reset_index(drop=True))
        if keepers_in_team:
            st.info(f"Keeper(s): {', '.join(keepers_in_team)}")
        else:
            st.warning("⚠️ Geen keeper in dit team")