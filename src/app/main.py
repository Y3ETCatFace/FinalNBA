from nba_api.stats.endpoints import playbyplayv3
import pandas as pd
import os
from pathlib import Path

"""
str_game_id = "0022401136"

path = "~/Apps/FinalNBA/data/raw/gyat.csv"

# 1. Get the API response object
ra = playbyplayv3.PlayByPlayV3(start_period=1, end_period=10, game_id="0022401136")

# 2. Extract the actual DataFrame from the object
# .get_data_frames() returns a LIST of DataFrames. 
# For PlayByPlayV3, the data you want is at index [0].
df = ra.get_data_frames()[0]

pd.DataFrame(df).to_csv(path, index=True)
"""
