
import pandas as pd
import random

def generate_teams(df_spelers, team_count=2):
    # Converteer rating naar float
    df_spelers["rating"] = df_spelers["rating"].astype(float)

    # Zet keepers op aparte lijst
    keepers = df_spelers[df_spelers["keeper"].str.lower() == "ja"].copy()
    veldspelers = df_spelers[df_spelers["keeper"].str.lower() != "ja"].copy()

    # Shuffle voor randomisering
    keepers = keepers.sample(frac=1).reset_index(drop=True)
    veldspelers = veldspelers.sample(frac=1).reset_index(drop=True)

    # Initialiseer lege teams
    teams = [[] for _ in range(team_count)]
    team_ratings = [0] * team_count

    # Verdeel de keepers zo eerlijk mogelijk
    for i, (_, keeper) in enumerate(keepers.iterrows()):
        team_index = i % team_count
        teams[team_index].append(keeper)
        team_ratings[team_index] += keeper["rating"]

    # Verdeel veldspelers met rating balancing
    for _, speler in veldspelers.iterrows():
        # Zoek team met laagste totaalrating
        team_index = team_ratings.index(min(team_ratings))
        teams[team_index].append(speler)
        team_ratings[team_index] += speler["rating"]

    # Maak DataFrames met overzicht per team
    team_dataframes = []
    for i, team in enumerate(teams):
        df_team = pd.DataFrame(team)
        if not df_team.empty:
            avg_rating = round(df_team["rating"].mean(), 2)
            df_team["keeper"] = df_team["keeper"].str.lower()
            df_team = df_team[["naam", "rating", "keeper"]]
            df_team.loc[len(df_team.index)] = ["Gemiddelde", avg_rating, ""]
        team_dataframes.append(df_team)

    return team_dataframes
