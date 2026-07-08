from collections import deque
import numpy as np
from tools.config import avg_opp_elo, is_home, days_since, is_back_to_back, games_played, distance_traveled, top_ten, create_flip
from utils import geo, calculate_elo, get_connection, sql_script, create_elo
from statistics import mean
import pandas as pd
from geopy.distance import geodesic

sql_lib = 'src/tools'
grain = 'game_id, team_id'


#--------------------------------------------------------------
def create_avg_opp_elo(df):
    df = create_elo(df)
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
    df.drop(columns=['opponent_id', 'elo'], inplace=True) #-------------------------------------------
    con.sql(f'CREATE TABLE training_data AS SELECT * FROM df')
    

def create_is_home(con):
    df = con.sql(f'SELECT {grain}, matchup FROM all_games').df()
    df["is_home"] = np.where(df['matchup'].str.contains('vs'), 1, np.where(df['matchup'].str.contains('@'), 0, np.nan))
    con.execute('ALTER TABLE training_data ADD COLUMN is_home FLOAT')
    con.execute('UPDATE training_data t SET is_home = d.is_home FROM df d WHERE d.game_id = t.game_id AND d.team_id = t.team_id')

def create_days_since(con):
    con.sql(sql_script(f'{sql_lib}/days_since.sql'))

def create_is_back_to_back(con):
    con.sql(sql_script(f'{sql_lib}/back_to_back.sql'))

def create_games_played(con):
    con.sql(sql_script(f'{sql_lib}/games_played.sql'))

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
        
def create_top_ten(con):
    df = con.sql(sql_script(f'{sql_lib}/top_ten.sql')).df()
    df = df.pivot(index=['team_id', 'game_id'], columns='rnk', values = [x for x in df.columns if x not in ['team_id', 'game_id', 'rnk']])
    df.reset_index(inplace=True)
    df.columns = [x[0] if x[0] in ['team_id', 'game_id'] else f'{x[0]}_{x[1]}' for x in df.columns]
    for col in [c for c in df.columns if c not in ['game_id', 'team_id']]:
        con.execute(f'ALTER TABLE training_data ADD column {col} FLOAT')
        con.execute(f'UPDATE training_data t SET {col} = f.{col} FROM df f WHERE t.game_id = f.game_id AND t.team_id = f.team_id')

def flip(con):
    cols = con.sql(f'SELECT * FROM training_data').columns
    filt_col = [x for x in cols if x not in ['plus_minus', 'game_id', 'team_id', 'is_home', 'outcome']]
    flip_string_update = ', '.join(f'opponent_{col} = opp.{col}' for col in filt_col)
    flip_string_alter = "; ".join(f'ALTER TABLE training_data ADD COLUMN "opponent_{col}" FLOAT' for col in filt_col)
    con.execute(f'{flip_string_alter}')
    con.execute(f'UPDATE training_data t SET {flip_string_update} FROM training_data opp WHERE t.game_id = opp.game_id AND t.team_id != opp.team_id')
    print(con.sql('SELECT * FROM training_data').columns)

if __name__ == "__main__":
    con = get_connection()
    if avg_opp_elo:
        df = con.sql(f"SELECT {grain}, season_id, plus_minus, opponent_id CASE WHEN plus_minus > 0 THEN 1 ELSE 0 END as outcome FROM all_games ORDER BY game_date, game_id").df()
        create_avg_opp_elo(df)
    if is_home:    
        create_is_home(con)
    if days_since:
        create_days_since(con)
    if is_back_to_back:    
        create_is_back_to_back(con)
    if games_played:
        create_games_played(con)
    if distance_traveled:
        create_distance_travled(con)
    if top_ten:
        create_top_ten(con)
    if create_flip:
        print(f'flip is {flip}')
        flip(con)
    

