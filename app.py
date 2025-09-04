import streamlit as st
import pandas as pd
import requests
from team_generator import generate_teams

# === CONSTANTEN ===
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec"

# === TITEL EN INPUT ===
st.title("🏀 Bounceball TEAMS")

names_input = st.text_area("Voer spelersnamen in (gescheiden door komma's):", placeholder="bijv. Roy, Dieuwke, Anjo")
team_count = st.number_input("Aantal teams:", min_value=2, max_value=10, value=2, step=1)

# === KNOP ===
if st.button("Maak teams"):
    try:
        spelers_namen = [naam.strip().lower() for naam in names_input.split(",") if naam.strip()]
        
        # === Ophalen van gegevens van Google Sheets ===
        response = requests.get(SCRIPT_URL)
        data = response.json()

        # === DataFrames bouwen ===
        df_spelers = pd.DataFrame(data)
        df_spelers["naam_lower"] = df_spelers["naam"].str.lower()
        df_spelers = df_spelers[df_spelers["naam_lower"].isin(spelers_namen)].copy()
        df_spelers.drop(columns=["naam_lower"], inplace=True)

        if df_spelers.empty:
            st.error("⚠️ Geen spelers gevonden met de opgegeven namen.")
        else:
            # === Teams genereren ===
            teams = generate_teams(df_spelers, team_count=team_count)

            # === Teams tonen ===
            for i, team in enumerate(teams, 1):
                st.subheader(f"Team {i}")
                st.table(team)

    except requests.exceptions.RequestException:
        st.error("❌ Fout bij het ophalen van data. Controleer je internetverbinding of de script-URL.")
    except ValueError:
        st.error("❌ De gegevens van het Google Script zijn niet in JSON-formaat.")
    except Exception as e:
        st.error(f"❌ Onverwachte fout: {e}")
            for speler in team["players"]:
                keeper_str = " (keeper)" if speler["keeper"] else ""
                st.write(f"- {speler['naam']} (rating: {speler['rating']}){keeper_str}")
