from collections import deque
import numpy as np
import duckdb as db
from setup_database import db_path
from tool_config import avg_opp_elo, is_home, days_since, is_back_to_back, games_played, geo, distance_travled
from statistics import mean
import pandas as pd
from geopy.distance import geodesic
import time


grain = 'game_id, team_id'

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

def sql_script(path):
    with open(path) as sql:
        return sql.read()

def create_avg_opp_elo_col(con):
    df = con.sql(f"SELECT {grain}, season_id, CASE WHEN plus_minus > 0 THEN 1 ELSE 0 END as outcome, matchup FROM all_games ORDER BY game_date, game_id").df()
    df['elo'] = pd.NA
    df['opponent_id'] = pd.array([pd.NA] * len(df), dtype='Int64')  # capital I
    for i in range(0, len(df), 2):
        id_a = df.iloc[i]['team_id']
        id_b = df.iloc[i+1]['team_id']
        df.at[i, 'opponent_id'] = id_b
        df.at[i+1, 'opponent_id'] = id_a
        outcome_a = df.iloc[i]['outcome']
        outcome_b = df.iloc[i+1]['outcome']
        new_a_season_id = df.iloc[i]['season_id']
        new_b_season_id = df.iloc[i+1]['season_id']
        a_season_id = id_season_id.get(id_a, None)
        b_season_id = id_season_id.get(id_b, None)
        a_elo = id_elo.get(id_a, 1500)
        b_elo = id_elo.get(id_b, 1500)
        outcome = 1 if outcome_a > outcome_b else 0
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
#--------------------------------------------------------------
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
    df.drop(columns=['opponent_id', 'matchup', 'season_id'], inplace=True) #-------------------------------------------
    con.sql('CREATE TABLE training_data AS SELECT * FROM df')

def create_is_home(con):
    df = con.sql(f'SELECT {grain}, matchup FROM all_games').df()
    df["is_home"] = np.where(df['matchup'].str.contains('vs'), 1, np.where(df['matchup'].str.contains('@'), 0, np.nan))
    con.execute('ALTER TABLE training_data ADD COLUMN is_home FLOAT')
    con.execute('UPDATE training_data t SET is_home = d.is_home FROM df d WHERE d.game_id = t.game_id AND d.team_id = t.team_id')

def create_days_since(con):
    con.sql(sql_script('src/tools/days_since.sql'))

def create_is_back_to_back(con):
    con.sql(sql_script('src/tools/back_to_back.sql'))

def create_games_played(con):
    con.sql(sql_script('src/tools/games_played.sql'))

def create_distance_travled(con):
    coords = []
    df = con.sql(f'SELECT team_id, game_id, opponent_id, matchup FROM all_games ORDER BY game_date').df()
    geo_series = pd.DataFrame.from_dict(geo, orient = 'index')
    look_up_ids = pd.Series(np.where(df['matchup'].str.contains('vs.'), df['team_id'], np.where(df['matchup'].str.contains('@'), df['opponent_id'], 0)))
    last_look_up_ids = look_up_ids.groupby(df['team_id']).shift(1).astype('Int64')
    current_coords = look_up_ids.map(geo_series['coords'])
    last_coords = last_look_up_ids.map(geo_series['coords'])
    for i in range(len(df)):
        curent = current_coords.loc[i]
        last = last_coords.loc[i]
        distance_travled = (str(geodesic(last, curent))[:-3] if not pd.isna(last) else 0)
        coords.append(distance_travled)
    df['distance_traveled'] = coords
    df.drop(columns = ['matchup', 'opponent_id'], inplace = True)
    con.sql('ALTER TABLE training_data ADD COLUMN distance_traveled FLOAT')
    con.sql('UPDATE training_data t SET distance_traveled = f.distance_traveled FROM df f WHERE t.game_id = f.game_id AND t.team_id = f.team_id')
    con.sql('SELECT * FROM training_data').show()
        
    
def flip(con):
    cols = con.sql(f'SELECT * FROM training_data').columns
    filt_col = [x for x in cols if x not in ['plus_minus', 'game_id', 'team_id, is_home']]
    flip_string_update = ', '.join(f'opponent_{col} = opp.{col}' for col in filt_col)
    flip_string_alter = "; ".join(f'ALTER TABLE training_data ADD COLUMN opponent_{col} FLOAT' for col in filt_col)
    print(flip_string_alter)
    con.execute(f'{flip_string_alter}')
    con.execute(f'UPDATE training_data t SET {flip_string_update} FROM training_data opp WHERE t.game_id = opp.game_id AND t.team_id != opp.team_id')


if __name__ == "__main__":
    con = db.connect(db_path)
    if avg_opp_elo:
        create_avg_opp_elo_col(con)
    if is_home:    
        create_is_home(con)
    if days_since:
        create_days_since(con)
    if is_back_to_back:    
        create_is_back_to_back(con)
    if games_played:
        create_games_played(con)
    if distance_travled:
        create_distance_travled(con)
    

