import duckdb

con = duckdb.connect("data/db/nba.db")

df = con.execute("""
    SELECT *
    EXCLUDE (team_id, game_id, season_id)
    FROM training_data
""").df()

# Optional: export to CSV
df.to_csv("training_data.csv", index=False)