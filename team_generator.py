import numpy as np

def generate_teams(df_spelers, df_regels, team_count):
    import random
    spelers = df_spelers.to_dict(orient="records")

    # Keepers verdelen
    keepers = [s for s in spelers if str(s["keeper"]).strip().lower() == "ja"]
    veldspelers = [s for s in spelers if s not in keepers]
    random.shuffle(keepers)
    random.shuffle(veldspelers)

    teams = [[] for _ in range(team_count)]

    # Verdeel keepers
    for i, keeper in enumerate(keepers):
        teams[i % team_count].append(keeper)

    # Verdeel overige spelers
    i = 0
    for speler in veldspelers:
        teams[i % team_count].append(speler)
        i += 1

    # Pas groepsregels toe (alleen 'samen: nee' voor nu)
    regels_niet_samen = df_regels[df_regels["samen"].str.lower() == "nee"]
    for _, regel in regels_niet_samen.iterrows():
        speler1, speler2 = regel["Speler1"], regel["Speler2"]
        for team in teams:
            namen = [s["naam"].lower() for s in team]
            if speler1.lower() in namen and speler2.lower() in namen:
                # Regel overtreden - geen herindeling (voor demo)
                pass

    # Bereken gemiddelden
    result = []
    for team in teams:
        ratings = [float(s["rating"]) for s in team]
        avg = np.mean(ratings) if ratings else 0
        result.append({
            "players": team,
            "average_rating": avg
        })

    return result