from collections import deque
import sys

from numpy import average
import pandas as pd
import duckdb as db

db_path = "data/db/nba.db"
con = db.connect(db_path)


con.sql(f"SELECT * FROM active_players WHERE team_abbrev = 'BKN' and season_id = 22024 ORDER BY player_name").show()

if input("exit? ") == "y":
    sys.exit()
for i in range(0, 30, 5):
    new = con.sql(f"SELECT plus_minus from master_nba WHERE {i} <= reb AND reb < {i + 5}").df()
    fah = new['plus_minus'].to_list()

    print(f'Average plus minus for {i} to {i + 5} rebounds is: {average(fah)}')
