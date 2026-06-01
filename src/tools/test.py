import duckdb as db
import pandas as pd
from geopy.distance import geodesic

con = db.connect('data/db/nba.db')
# (lat, lon) for two airports
new_york = (40.6413, -73.7781)   # JFK
london   = (51.4700, -0.4543)    # Heathrow

distance = geodesic(new_york, london)
print(distance)
con.sql('SELECT * FROM training_data WHERE is_back_to_back = 0').show()
#con.sql('DROP TABLE training_data')
#con.sql("DROP TABLE training_data")
class player:
    def __init__(self, height, weight):
        self.height = height
        self.weight