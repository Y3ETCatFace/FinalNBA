import pandas as pd
from nba_api.stats.endpoints import LeagueGameFinder, ScoreboardV3, CommonTeamRoster, PlayerGameLog, PlayerGameLogs
import duckdb as db
from tools.utils import MASTER_MAP, TABLE_SCHEMA, calculate_elo, clean_df, sql_script, get_connection, clean_data
from tools.data_creation import master_game_id_endpoint
from statistics import mean
from tools.features import create_elo
from time import sleep


con = get_connection()
sql_lib = 'src/tools'

current_id = con.sql('SELECT max(season_id) FROM all_games').fetchall()[0][0]

try:
    season = f'{str(current_id + 1)[1:]}-{(int(str(current_id + 1)[-2:])+1)}'
    LeagueGameFinder(season_nullable = str(season), season_type_nullable = "Regular Season")
except Exception:
    season = f'{str(current_id)[1:]}-{(int(str(current_id)[-2:])+1)}'

df = LeagueGameFinder(season_nullable = str(season), season_type_nullable = "Regular Season").get_data_frames()[0]

current_games = [x[0] for x in con.sql('SELECT game_id FROM all_games').fetchall()]
df = df[~df['GAME_ID'].isin(current_games)]
if not df.empty:
    print('not empty')
    master_string = f'{clean_data(df.columns, 'all_games')} '
    print(master_string)
    con.execute(f'INSERT INTO all_games SELECT {master_string} FROM df')
else:
    print('No new games')

df = con.sql(f"SELECT team_id, game_id, season_id, CASE WHEN plus_minus > 0 THEN 1 ELSE 0 END as outcome FROM all_games ORDER BY game_date, game_id").df()

dff = create_elo(df)

team_ids = ['1610612755']

#'1610612755'

for team in team_ids:
    players = CommonTeamRoster(team_id=team_ids[0]).get_data_frames()[0]['PLAYER_ID'].astype(str).tolist()
    game_id_set = set()
    for player in players:
        print(f'trying {player}')
        ids = PlayerGameLog(player_id = player).get_data_frames()[0]['Game_ID']
        sleep(.5)
        game_id_set.update(ids)
        try:
            con.sql('SELECT * FROM prime')
        except:
            sql_script(f'{sql_lib}/prime.sql')
    
    for typee in ['advanced', 'defensive', 'fourfactors', 'hustle']:
        df_list = []
        for game in game_id_set:
            if game not in con.sql(f'SELECT game_id FROM {typee}').fetchall():
                df = clean_df(master_game_id_endpoint(current_id = game, data_type = typee), typee)
                df_list.append(df)
        df = pd.concat(df_list)
        if not any(item in df.columns for item in con.sql(f'SELECT * FROM prime').columns):
            print(f'joining {typee}')
            con.execute(f'SELECT *, ROW_NUMBER() OVER(PARTITION BY game_id, player_id ORDER BY game_date DESC AS rnk FROM prime l LEFT JOIN df r ON r.game_id = l.game_id AND r.player_id = l.player_id')





