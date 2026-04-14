import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats

df = leaguedashplayerstats.LeagueDashPlayerStats(season="2024-25",season_type_all_star="Regular Season").get_data_frames()[0]

df.to_csv("player_stats.csv", index = False)