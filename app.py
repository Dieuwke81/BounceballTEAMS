import streamlit as st
import pandas as pd
import requests

st.title("Bounceball TEAMS")

# Invoer van namen
names_input = st.text_input("Voer spelersnamen in (gescheiden door komma's):", "")
team_count = st.number_input("Aantal teams:", min_value=2, max_value=20, value=2, step=1)
maak_teams = st.button("Maak teams")

if maak_teams:
    spelers_namen = [naam.strip().lower() for naam in names_input.split(",") if naam.strip()]

    url = "https://script.google.com/macros/s/AKfycbzesNHiNUOmCCiBVMgnULXWdHANF_rdFDJu8ag04O7C_SNyzXvWphfZponYj_nTSlgZ/exec"

    try:
        response = requests.get(url)
        data = response.json()  # <== dit is nu een LIST, geen dict

        df_spelers = pd.DataFrame(data)

        # Normaliseer namen
        df_spelers["naam_lower"] = df_spelers["naam"].str.lower()
        df_spelers = df_spelers[df_spelers["naam_lower"].isin(spelers_namen)].copy()
        df_spelers.drop(columns=["naam_lower"], inplace=True)

        if df_spelers.empty:
            st.error("Geen spelers gevonden met de opgegeven namen.")
        else:
            st.write("✅ Spelers ingeladen:")
            st.dataframe(df_spelers)

            # TODO: Voeg hier je team-generatie logica toe
            st.success(f"Teams zouden nu gegenereerd worden (nog te implementeren).")

    except requests.exceptions.RequestException as e:
        st.error(f"Fout bij het ophalen van data: {e}")
    except ValueError as e:
        st.error(f"Ongeldige JSON ontvangen: {e}")
