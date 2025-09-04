import pandas as pd
import random

def generate_teams(df_spelers, df_regels, aantal_teams):
    df_spelers["rating"] = df_spelers["rating"].astype(float)
    spelers = df_spelers.sort_values(by="rating", ascending=False).to_dict(orient="records")

    teams = [[] for _ in range(aantal_teams)]
    total_ratings = [0] * aantal_teams

    for speler in spelers:
        idx = total_ratings.index(min(total_ratings))
        teams[idx].append(speler)
        total_ratings[idx] += speler["rating"]

    df_teams = [pd.DataFrame(team) for team in teams]
    return df_teams