import streamlit as st
import pandas as pd
import requests

# URL naar jouw werkende Google Apps Script
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

    # Zorg dat rating numeriek is
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)

    # Verdeel spelers
    keepers = df[df["keeper"] == "ja"].sort_values(by="rating", ascending=False).reset_index(drop=True)
    veldspelers = df[df["keeper"] != "ja"].sort_values(by="rating", ascending=False).reset_index(drop=True)

    teams = [[] for _ in range(num_teams)]
    team_ratings = [0.0 for _ in range(num_teams)]

    # Verdeel keepers
    for i, keeper in keepers.iterrows():
        idx = i % num_teams
        teams[idx].append(keeper)
        team_ratings[idx] += keeper["rating"]

    # Verdeel overige spelers naar laagste teamgemiddelde
    for _, speler in veldspelers.iterrows():
        idx = team_ratings.index(min(team_ratings))
        teams[idx].append(speler)
        team_ratings[idx] += speler["rating"]

    # Toon resultaten
    st.subheader("📋 Teamindeling")

    for i, team in enumerate(teams):
        team_df = pd.DataFrame(team)
        avg_rating = round(team_df["rating"].mean(), 2)
        keepers_in_team = team_df[team_df["keeper"] == "ja"]["naam"].tolist()

        st.markdown(f"### 🟢 Team {i + 1} (Gem. rating: {avg_rating})")
        st.dataframe(team_df[["naam", "rating", "keeper"]].reset_index(drop=True))
        if keepers_in_team:
            st.info(f"Keeper(s): {', '.join(keepers_in_team)}")
        else:
            st.warning("⚠️ Geen keeper in dit team")