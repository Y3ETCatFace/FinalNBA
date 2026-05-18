import duckdb
import os
from pathlib import Path
import table_schema
import normilize
import pandas as pd
import sys

"""
    "active_players": "data/raw/*/active_players.csv",
    "gamelog": "data/raw/*/gamelog.csv",
    "all_games": "data/raw/*/all_games.csv",
    "playbyplay": "data/raw/*/PlaybyPlayData/*.csv",
    "advanced": "data/raw/*/advanced/*.csv",
    "defensive": "data/raw/*/defensive/*.csv",
    "fourfactors": "data/raw/*/fourfactors/*.csv",
    "hustle": "data/raw/*/hustle/*.csv",
"""

db_path = "data/db/nba.db"
raw_path = "data/raw/*/"
def get_connection():
    if not os.path.exists(db_path):
        Path(db_path).parent.mkdir(exist_ok=True, parents=True)
    return duckdb.connect(db_path)
    
RENAMES = normilize.MASTER_MAP
whitebool = True

def data_ingest(con):
    if not os.path.exists(db_path):
        Path(db_path).parent.mkdir(exist_ok=True, parents=True)
    for data_type, meta in table_schema.TABLE_SCHEMA.items():
        path = f"{raw_path}{meta["path"]}"
        whitelist = meta['whitelist']
        george = con.read_csv(path, quotechar='"')
        col = george.columns
        filter = {f: s for f, s in RENAMES.items() if f in col and (s in whitelist if whitebool else True)}
        master_string = ", ".join(f"{f} as {s}" for f, s in filter.items())
        con.sql(f"CREATE TABLE {data_type} AS SELECT {master_string} FROM george")
        print(f"\n{data_type} succesfully created!\n")

if __name__ == "__main__":
    with get_connection() as con:
        data_ingest(con)

   
