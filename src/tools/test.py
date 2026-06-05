import os

import duckdb as db
import pandas as pd
from geopy.distance import geodesic
from nba_api.stats.endpoints import CommonAllPlayers, CommonPlayerInfo

con = db.connect('data/db/nba.db')

print(con.sql('SELECT season_id FROM training_data').show())

con.execute('DROP TABLE training_data')

con.sql('SHOW TABLES').show()




#con.sql('DROP TABLE training_data')
#con.sql("DROP TABLE training_data")
class player:
    def __init__(self, height, weight):
        self.height = height
        self.weight