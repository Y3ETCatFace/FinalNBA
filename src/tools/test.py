import duckdb as db
import pandas as pd

con = db.connect('data/db/nba.db')
#con.sql('SELECT * FROM training_data WHERE days_since_last = 1').show()
con.sql('SELECT * FROM training_data WHERE games_played = 82').show()
#con.sql("DROP TABLE training_data")
class player:
    def __init__(self, height, weight):
        self.height = height
        self.weight