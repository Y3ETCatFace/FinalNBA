import duckdb as db
from setup_database import db_path
from normilize import MASTER_MAP
from table_schema import TABLE_SCHEMA
import sys

con = db.connect(db_path)
path = 'data/raw/*/all_games.csv'
george = con.read_csv(path, quotechar='"')
col = george.columns
filter = {f: s for f, s in MASTER_MAP.items() if f in col and s in TABLE_SCHEMA['all_games']['whitelist'] }
master_string = ', '.join(f"{f} AS {s}" for f, s in filter.items())

df = con.sql(f"SELECT plus_minus, game_id, game_date, team_id FROM all_games ORDER BY game_date ASC, game_id").df()

seen = set()

def calculate_elo(elo_a, elo_b, outcome, k=20):
    expected = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    new_elo_a = elo_a + k * (outcome - expected)
    new_elo_b = elo_b + k * ((1 - outcome) - (1 - expected))
    return new_elo_a, new_elo_b

for i in range(0, len(df), 2):
    id_a = df.loc[i, 'team_id']
    id_b = df.loc[i+1, 'team_id']
    plus_minus_a = df.loc[i, 'plus_minus']
    plus_minus_b = df.loc[i+1, 'plus_minus']
    for team_id in [id_a, id_b]:
        if team_id not in seen:
            seen.add(team_id)
            df.loc[i if team_id == id_a else i+1, 'elo'] = 1500
        elif plus_minus_a + plus_minus_b != 0:
            sys.exit()
        else:
            a_elo = df.loc[i-2, 'elo']
            b_elo = df.loc[i-1, 'elo']
            outcome = 1 if plus_minus_a > 0 else 0
            new_a_elo, new_b_elo = calculate_elo(a_elo, b_elo, outcome)

def update_elo(row):
    team_id = row['team_id']
    if team_id not in seen:
        seen.add(team_id)
        return 1500
    else:
        # Calculate new ELO based on previous games
        # This is a placeholder, you would need to implement the logic to calculate the new ELO based on the game outcome
        return big_row['elo']  # Replace with actual ELO calculation

print(len(seen))
#con.sql(f"INSERT INTO all_games SELECT {master_string} from george")
#con.sql('DROP TABLE nba_training')
#con.sql("SELECT * FROM nba_training where season_id != 22019 ORDER BY game_date").show()
#con.sql(f"CREATE TABLE nba_training AS SELECT game_date, season_id, team_abbrev, team_id, plus_minus FROM all_games")
#con.sql(f"INSERT INTO nba_training SELECT {master_string} from all_games WHERE season_id = 22019")
#con.sql(f"CREATE TABLE nba_training_data AS SELECT ")
#game_ids = con.sql("SELECT game_id from all_games WHERE season_id = 22020").list()
# id = con.sql("CREATING TABLE training_data as ")