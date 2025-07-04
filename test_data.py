import matplotlib
matplotlib.use('Agg')  # Ensure no GUI requirement

import random
import pandas as pd
import matplotlib.pyplot as plt
import os

NUM_TEAMS = 7
TEAM_SIZE = 3
NUM_ROUNDS = 6

def generate_team_data(num_teams, team_size, num_rounds):
    teams = []
    for t in range(num_teams):
        team = {'team_id': t+1, 'players': []}
        for p in range(team_size):
            player = {'player_id': f'Team {t+1} Player {p+1}', 'rounds': []}
            for r in range(num_rounds):
                player['rounds'].append({'kills': 0, 'deaths': 0, 'damage': 0})
            team['players'].append(player)
        team['placements'] = [0]*num_rounds
        teams.append(team)
    return teams

def get_kills_template(num_teams):
    max_kills = 20
    min_kills = 6
    if num_teams == 1:
        return [max_kills]
    step = (max_kills - min_kills) / max(1, (num_teams - 1))
    # Make sure the numbers are ints and descending
    return [int(round(max_kills - i*step)) for i in range(num_teams)]

def assign_stats_and_placements(teams, num_rounds):
    num_teams = len(teams)
    for r in range(num_rounds):
        team_indices = list(range(num_teams))
        random.shuffle(team_indices)

        kills_template = get_kills_template(num_teams)

        round_team_stats = []

        for idx, team_idx in enumerate(team_indices):
            team = teams[team_idx]
            total_kills = kills_template[idx]
            kills_left = total_kills

            for i, player in enumerate(team['players']):
                if i == len(team['players']) - 1:
                    kills = kills_left
                else:
                    max_kills = min(12, kills_left)
                    kills = random.randint(0, max_kills)
                    kills_left -= kills

                deaths = random.randint(0, 2 + idx // 3)
                damage = kills * random.randint(350, 600) + random.randint(0, 200)
                player['rounds'][r] = {
                    'kills': kills,
                    'deaths': deaths,
                    'damage': damage
                }

            round_team_stats.append((team, sum(p['rounds'][r]['kills'] for p in team['players'])))

        round_team_stats.sort(key=lambda x: x[1], reverse=True)
        for place, (team, _) in enumerate(round_team_stats, start=1):
            team['placements'][r] = place

def round_to_dataframe(team, round_index):
    rows = []
    for p in team['players']:
        rnd = p['rounds'][round_index]
        rows.append({
            'Player': p['player_id'],
            'Kills': rnd['kills'],
            'Deaths': rnd['deaths'],
            'Damage': rnd['damage'],
            'Placement': team['placements'][round_index] if rows == [] else ""
        })
    df = pd.DataFrame(rows)
    return df

def save_team_round_image(team, round_index, folder="team_images"):
    team_folder = os.path.join(folder, f"team_{team['team_id']}")
    os.makedirs(team_folder, exist_ok=True)
    df = round_to_dataframe(team, round_index)
    fig, ax = plt.subplots(figsize=(7, 1 + len(df)*0.8))
    ax.axis('off')
    tbl = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(12)
    tbl.scale(1.1, 1.7)
    plt.title(f"Team {team['team_id']} - Round {round_index+1}")
    plt.tight_layout()
    plt.savefig(os.path.join(team_folder, f"round_{round_index+1}.png"))
    plt.close()

# ---- MAIN ----
teams = generate_team_data(NUM_TEAMS, TEAM_SIZE, NUM_ROUNDS)
assign_stats_and_placements(teams, NUM_ROUNDS)
for team in teams:
    for round_index in range(NUM_ROUNDS):
        save_team_round_image(team, round_index)

print("Images saved in 'team_images/team_{team_id}/round_{n}.png' folders with correct per-round randomized placements.")
