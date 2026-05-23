from collections import deque

import duckdb as db
from setup_database import db_path
from table_schema import MASTER_MAP
from table_schema import TABLE_SCHEMA
import sys
from statistics import mean
import pandas as pd

TEAM_ID_MAP = {'BKN': 1610612751, 'PHI': 1610612755, 'IND': 1610612754, 'UTA': 1610612762, 'DET': 1610612765, 'MIN': 1610612750, 'BOS': 1610612738, 'WAS': 1610612764, 'NYK': 1610612752, 'TOR': 1610612761, 'LAC': 1610612746, 'DAL': 1610612742, 'MIL': 1610612749, 'MEM': 1610612763, 'CHA': 1610612766, 'ATL': 1610612737, 'HOU': 1610612745, 'SAC': 1610612758, 'LAL': 1610612747, 'NOP': 1610612740, 'POR': 1610612757, 'GSW': 1610612744, 'PHX': 1610612756, 'SAS': 1610612759, 'ORL': 1610612753, 'OKC': 1610612760, 'MIA': 1610612748, 'DEN': 1610612743, 'CLE': 1610612739, 'CHI': 1610612741}


def calculate_elo(elo_a, elo_b, outcome, 
                  a_season_id, b_season_id, 
                  a_last_season_id, b_last_season_id,
                  a_season_game_count, b_season_game_count,
                  roster_continuity_a=1.0, roster_continuity_b=1.0, 
                  k=20):
    
    if a_season_id != a_last_season_id:
        elo_a = elo_a + (1500 - elo_a) * (1 - roster_continuity_a)
        k_a = k * (1 + max(0, (5 - a_season_game_count) / 5))
    else:
        k_a = k

    if b_season_id != b_last_season_id:
        elo_b = elo_b + (1500 - elo_b) * (1 - roster_continuity_b)
        k_b = k * (1 + max(0, (5 - b_season_game_count) / 5))
    else:
        k_b = k

    expected = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    new_elo_a = elo_a + k_a * (outcome - expected)
    new_elo_b = elo_b + k_b * ((1 - outcome) - (1 - expected))
    return new_elo_a, new_elo_b

id_elo = {}
id_season_id = {}

def create_opp_id_col_and_elo(df):
    df['elo'] = pd.NA
    df['opponent_id'] = pd.array([pd.NA] * len(df), dtype='Int64')  # capital I
    for i in range(0, len(df), 2):
        id_a = df.iloc[i]['team_id']
        id_b = df.iloc[i+1]['team_id']
        df.at[i, 'opponent_id'] = id_b
        df.at[i+1, 'opponent_id'] = id_a
        plus_minus_a = df.iloc[i]['plus_minus']
        plus_minus_b = df.iloc[i+1]['plus_minus']
        new_a_season_id = df.iloc[i]['season_id']
        new_b_season_id = df.iloc[i+1]['season_id']
        a_season_id = id_season_id.get(id_a, None)
        b_season_id = id_season_id.get(id_b, None)
        a_elo = id_elo.get(id_a, 1500)
        b_elo = id_elo.get(id_b, 1500)
        outcome = 1 if plus_minus_a > plus_minus_b else 0
        if new_a_season_id != a_season_id:
            a_season_game_count = 1
        elif a_season_game_count < 5:
            a_season_game_count += 1
        if new_b_season_id != b_season_id:
            b_season_game_count = 1
        elif b_season_game_count < 5:
            b_season_game_count += 1
        new_a_elo, new_b_elo = calculate_elo(a_elo, b_elo, outcome, new_a_season_id, new_b_season_id, a_season_id, b_season_id, a_season_game_count, b_season_game_count) #Outcome 1 means team A won
        df.at[i, 'elo'] = new_a_elo
        df.at[i+1, 'elo'] = new_b_elo
        id_elo[id_a] = new_a_elo
        id_elo[id_b] = new_b_elo
        id_season_id[id_a] = new_a_season_id
        id_season_id[id_b] = new_b_season_id
    return df

def create_avg_opp_elo_col(df):
    elo_window = {}
    for i in range(len(df)):
        even = -1 if i % 2 != 0 else None
        id = df.iloc[i]['team_id']
        opp_id = (df.iloc[i]['opponent_id'])
        last_15_elo = list(elo_window.get(id, []))[:even][-15:] # Exclude current game
        average_opp_elo = mean(last_15_elo) if last_15_elo else 1500
        df.at[i, 'avg_opp_elo'] = average_opp_elo
        if opp_id not in elo_window:
            elo_window[opp_id] = deque(maxlen=16)
        elo_window[opp_id].append(df.iloc[i]['elo'])
    return df

if __name__ == "__main__":
    con = db.connect(db_path)
    df = con.sql(f"SELECT plus_minus, game_id, season_id, team_id, matchup, game_date FROM all_games ORDER BY game_date, game_id").df()
    
    df = create_opp_id_col_and_elo(df)
    df = create_avg_opp_elo_col(df)
    




#path = 'data/raw/*/all_games.csv'
#george = con.read_csv(path, quotechar='"')
#col = george.columns
#filter = {f: s for f, s in MASTER_MAP.items() if f in col and s in TABLE_SCHEMA['all_games']['whitelist'] }
#master_string = ', '.join(f"{f} AS {s}" for f, s in filter.items())
#con.sql(f"INSERT INTO all_games SELECT {master_string} from george")
#con.sql('DROP TABLE nba_training')
#con.sql("SELECT * FROM nba_training where season_id != 22019 ORDER BY game_date").show()
#con.sql(f"CREATE TABLE nba_training AS SELECT game_date, season_id, team_abbrev, team_id, plus_minus FROM all_games")
#con.sql(f"INSERT INTO nba_training SELECT {master_string} from all_games WHERE season_id = 22019")
#con.sql(f"CREATE TABLE nba_training_data AS SELECT ")
#game_ids = con.sql("SELECT game_id from all_games WHERE season_id = 22020").list()
# id = con.sql("CREATING TABLE training_data as ")