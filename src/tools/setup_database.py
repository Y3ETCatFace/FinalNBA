import duckdb
import os
from pathlib import Path

table = {
    "active_players": "data/raw/*/active_players.csv",
    "gamelog": "data/raw/*/gamelog.csv",
    "all_games": "data/raw/*/all_games.csv",
    "playbyplay": "data/raw/*/PlaybyPlayData/*.csv",
    "advanced": "data/raw/*/AdvancedData/*.csv",
    "defensive": "data/raw/*/DefensiveData/*.csv",
    "fourfactors": "data/raw/*/FourFactorsData/*.csv",
    "hustle": "data/raw/*/HustleData/*.csv",

}

db_path = "data/raw/db/nba.duckdb"

def get_connection():
    return duckdb.connect(db_path)

# ── Explicit renames: raw column name → normalized name ───────────────────────
# Only columns that need more than just .lower() are listed here.
# Everything else gets lowercased automatically.
RENAMES = {
    # pbp camelCase → snake_case
    "gameid":       "game_id",
    "personid":     "player_id",
    "teamid":       "team_id",
    "teamtricode":  "team_abbreviation",
    "actionnumber": "action_number",
    "shotvalue":    "shot_value",
    "scorehome":    "score_home",
    "scoreaway":    "score_away",
    "isfieldgoal":  "is_field_goal",
    "pointstotal":  "points_total",
    "actiontype":   "action_type",
    "shotdistance": "shot_distance",
    "shotresult":   "shot_result",
    "xlegacy":      "x",
    "ylegacy":      "y",
    "playernamei":  "player_name_initial",
    "actionid":     "action_id",
}


def normalize_col(raw_col: str) -> str:
    lower = raw_col.lower()
    return RENAMES.get(lower, lower)


def build_select(table_name: str, cols: list[str]) -> str:
    """
    Builds the SELECT clause for a table, applying renames.
    pbp.clock is parsed from ISO 8601 (PT06M32.00S) to seconds remaining in period.
    """
    select_cols = []

    for raw_col in cols:
        normalized = normalize_col(raw_col)

        # special case: parse clock to seconds remaining in period
        if table_name == "pbp" and raw_col.lower() == "clock":
            select_cols.append(
                f"(CAST(regexp_extract(\"{raw_col}\", 'PT(\\d+)M', 1) AS INTEGER) * 60"
                f" + CAST(regexp_extract(\"{raw_col}\", 'M(\\d+\\.?\\d*)S', 1) AS FLOAT))"
                f" AS clock_secs_remaining"
            )
            continue

        select_cols.append(f'"{raw_col}" AS {normalized}')

    return ", ".join(select_cols)

if __name__ == "__main__":
    # ── ensure DB directory exists ────────────────────────────────────────────
    if not os.path.exists("data/raw/db/"):
        Path("data/raw/db/").mkdir(parents=True, exist_ok=True)
        print("Database directory created\n")
    else:
        print("Database directory already exists\n")

    con = get_connection()
    existing = con.sql("SHOW TABLES").df()["name"].tolist()

    if not all(t in existing for t in table.keys()):

        for name, path in table.items():
            print(f"Loading {name} ...")

            # fetch raw column names from CSV headers only (LIMIT 0 = no data read)
            cols = con.sql(
                f"SELECT * FROM read_csv('{path}', union_by_name=true) LIMIT 0"
            ).columns

            select_str = build_select(name, cols)

            con.sql(f"""
                CREATE OR REPLACE TABLE {name} AS
                SELECT {select_str}
                FROM read_csv('{path}', union_by_name=true)
            """)

            row_count = con.sql(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            col_count = len(con.sql(f"SELECT * FROM {name} LIMIT 0").columns)
            print(f"  ✓  {row_count:,} rows  |  {col_count} cols\n")
    else:
        print("All tables already exist, skipping ingestion\n")
