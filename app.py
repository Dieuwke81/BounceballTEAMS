import streamlit as st
import pandas as pd
import requests
import random
import copy

DATA_URL = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec"

st.set_page_config(page_title="Bounceball TEAMS", layout="centered")
st.image("https://raw.githubusercontent.com/roykok/Bounceball-teams/main/logo.png", width=150)
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

    keepers = df[df["keeper"] == "ja"].sort_values(by="rating", ascending=False).reset_index(drop=True)
    veldspelers = df[df["keeper"] != "ja"].reset_index(drop=True)

    total_players = len(keepers) + len(veldspelers)

    # Eerlijke teamgroottes (bijv. [4, 4, 5])
    base_size = total_players // num_teams
    extras = total_players % num_teams
    team_sizes = [base_size + 1 if i < extras else base_size for i in range(num_teams)]

    best_teams = None
    best_diff = float("inf")

    for _ in range(50000):
        temp_teams = [[] for _ in range(num_teams)]
        team_ratings = [0.0] * num_teams

        for i, keeper in keepers.iterrows():
            idx = i % num_teams
            temp_teams[idx].append(keeper)
            team_ratings[idx] += keeper["rating"]

        shuffled = veldspelers.sample(frac=1).reset_index(drop=True)

        pointers = [len(team) for team in temp_teams]
        team_indices = []
        for i, size in enumerate(team_sizes):
            team_indices.extend([i] * (size - pointers[i]))

        random.shuffle(team_indices)

        for idx, (_, speler) in zip(team_indices, shuffled.iterrows()):
            temp_teams[idx].append(speler)
            team_ratings[idx] += speler["rating"]

        team_avgs = [
            team_ratings[i] / len(temp_teams[i]) if len(temp_teams[i]) > 0 else 0
            for i in range(num_teams)
        ]
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