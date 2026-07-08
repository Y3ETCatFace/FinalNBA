import duckdb
import os
from pathlib import Path
from utils import TABLE_SCHEMA, clean_data, get_connection
from features import create_elo
import pandas as pd

db_path = "data/nba.db"
raw_path = "data/raw/*/"

    
whitebool = True

def data_ingest(con):
    if not os.path.exists(db_path):
        Path(db_path).parent.mkdir(exist_ok=True, parents=True)
    for data_type, meta in TABLE_SCHEMA.items():
        try:
            con.sql(f'SELECT * FROM {data_type}')
        except:
            path = f"{raw_path}{meta["path"]}"
            george = con.read_csv(path, quotechar = '"')
            master_string = clean_data(george.columns, data_type)
            con.sql(f"CREATE {'TEMP' if data_type not in ['active_players', 'biometrics', 'play_by_play', 'all_games'] else ''} TABLE {data_type} AS SELECT {master_string} FROM george")
            print(f"\n{data_type} succesfully created!\n")
        if data_type == 'all_games':
            try:
                con.sql('SELECT elo FROM all_games')
            except:
                df = con.sql(f"SELECT team_id, game_id, season_id, CASE WHEN plus_minus > 0 THEN 1 ELSE 0 END as outcome FROM all_games ORDER BY game_date, game_id").df().copy()
                print(df)
                df = create_elo(df)
                print(df)
                con.sql('ALTER TABLE all_games ADD COLUMN elo FLOAT')
                con.sql('UPDATE all_games a SET elo = b.elo FROM df b WHERE a.game_id = b.game_id AND a.team_id = b.team_id')

if __name__ == "__main__":
    with get_connection() as con:
        data_ingest(con)
        if 'master_nba' not in [x[0] for x in con.sql('SHOW TABLES').fetchall()]:
            con.sql('CREATE TABLE master_nba AS ' \
            'SELECT * FROM gamelog ' \
            'LEFT JOIN advanced USING (player_id, game_id) ' \
            'LEFT JOIN defensive USING (player_id, game_id) ' \
            'LEFT JOIN fourfactors USING (player_id, game_id) ' \
            'LEFT JOIN hustle USING (player_id, game_id)')
            
        for table in ['all_games', 'master_nba']:
            try:
                con.sql(f'SELECT opponent_id FROM {table}')
                print(f'Opponent_id already exists in {table}')
            except:
                con.execute(f'ALTER TABLE {table} ADD COLUMN opponent_id INT')
                con.execute(f"UPDATE {table} t SET opponent_id = opp.team_id FROM {table} opp WHERE t.game_id = opp.game_id AND t.team_id != opp.team_id")
               
