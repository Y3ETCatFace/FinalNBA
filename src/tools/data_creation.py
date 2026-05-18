import pandas as pd
from nba_api.stats.endpoints import LeagueDashPlayerStats
from nba_api.stats.endpoints import PlayerGameLogs
from nba_api.stats.endpoints import CommonPlayerInfo #Testing
from requests.exceptions import JSONDecodeError, ReadTimeout, ConnectTimeout, RequestException
from nba_api.stats.endpoints import PlayByPlayV3
from nba_api.stats.endpoints import LeagueGameFinder #Ground truth
from nba_api.stats.endpoints import BoxScoreFourFactorsV3
from nba_api.stats.endpoints import BoxScoreAdvancedV3
from nba_api.stats.endpoints import BoxScoreTraditionalV3
from nba_api.stats.endpoints import HustleStatsBoxScore
from nba_api.stats.endpoints import BoxScoreDefensiveV2
import os
import time
import sys
import random
from pathlib import Path
import requests

#config:
root = "/Users/austin/Apps/FinalNBA/data/raw/"
start_year = 2019
end_year = 2020
base_delay = 30
long_pause_time = 30
max_attempts = 5
# Assuming your column is named 'player_id'

def master_id_endpoint(game_id, endpoint):
    try:
        df = endpoint_map[endpoint](game_id=game_id, timeout=50).get_data_frames()[0 if endpoint!="hustle" else 1]
        return df
    except AttributeError as e:
        print(f"Game for {game_id} doesn't exist using endpoint {endpoint}. Creating blank csv")
        print(e)
        return pd.DataFrame()


def season_range(first, second):
    year_list = []
    for year in range(first, second):
        next_year = year + 1
        season_str = f"{year}-{str(next_year)[2:]}"
        year_list.append(season_str)
        
    return year_list

def backoff(data_type, current_id, attempt = 0):
    while attempt < max_attempts:
        print(f"Current attempt is {attempt}")
        try:
            attempt += 1
            wait_time = base_delay * (2 ** attempt)
            print(f"Attempt {attempt} waiting {wait_time}")
            time.sleep(wait_time)
            print("Wait complete...\nAttempting to reset api")
            master_id_endpoint(current_id, data_type)
            attempt = 0
            break
        except Exception as e:
            print(f"{e} Failed retry {attempt}/{max_attempts} ")
    else:
        print("api failure system quit")

def getRandom():
    if random.random() <= 0.5:
        year_list = season_range(start_year, end_year)
        def fourfactors(x):
            BoxScoreFourFactorsV3(game_id=x, timeout = 15).get_data_frames()[0]
        def playbyplay(x):
            PlayByPlayV3(game_id=x, start_period=1, end_period = 10).get_data_frames()[0]
        def gamelog(x):
            BoxScoreTraditionalV3(game_id=x, timeout = 15).get_data_frames()[0]
        def advanced(x):
            BoxScoreAdvancedV3(game_id=x, timeout = 15).get_data_frames()[0]
        total_itterations = random.randint(2, 4)
        for x in range(total_itterations):
            random_year = random.choice(year_list)
            df = pd.read_csv(f"{root}{random_year}/gamelog.csv", usecols=["GAME_ID"], dtype={'GAME_ID': str})
            random_list = df["GAME_ID"].to_list()
            random_game = random.choice(random_list)
            random_funcion = random.choice([fourfactors, playbyplay, gamelog, advanced])
            try:
                random_funcion(random_game)
                print(f"{x+1}/{total_itterations} successful for reset api")
            except Exception as e:
                print(f"failed...waiting 10 seconds for reset api: {e}")
                time.sleep(10)
                pass
            time.sleep(1)
    else:
        print("Random sleep")
        time.sleep(random.uniform(10, 20))

def calculate_percent_completion(num, den):
    return f"{(num/den)*100:.3f}%"

endpoint_map = {
    "fourfactors": BoxScoreFourFactorsV3,
    "playbyplay": PlayByPlayV3,
    "defensive": BoxScoreDefensiveV2,
    "hustle": HustleStatsBoxScore,
    "advanced": BoxScoreAdvancedV3,
    "gamelog": PlayerGameLogs
}

def creategameIDdata(data_type):
    long_pause_every = random.randint(70, 90)
    data_root = f"{root}{season}/{data_type}/"
    attempt = 0
    request_counter = 1
    game_id_df = pd.read_csv(all_games_path, usecols=["GAME_ID"], dtype={'GAME_ID': str})
    game_list = game_id_df['GAME_ID'].unique().tolist()
    random.shuffle(game_list)
    game_set = set(game_list)
    if not os.path.exists(data_root):
        Path(data_root).mkdir(exist_ok=True, parents=True)
    files = {os.path.splitext(f)[0] for f in os.listdir(data_root) if os.path.splitext(f)[0].isdigit()}
    if files == game_set:
        print("All " + data_type + " data matchs game_list for season " + season)
    else:
        current_game_data = len(os.listdir(data_root))
        total_game_data = len(game_list)
        print(f"Now buiding {data_type} data for {season}")
        while game_list:
            if request_counter == long_pause_every:
                long_pause_every = random.randint(70, 90)
                print("Waiting Safe Delay")
                time.sleep(long_pause_time)
                request_counter = 0
            current_id = game_list.pop()
            data_path = f"{data_root}{current_id}.csv"
            if os.path.exists(data_path):
                print(f"{data_type} Skipped! {calculate_percent_completion(current_game_data,total_game_data)}")
                continue
            try:
                request_counter += 1
                if random.random() < 0.02:
                    getRandom()     
                df = master_id_endpoint(current_id, data_type)
                time.sleep(random.uniform(0.8, 1.6))
            except (ValueError, JSONDecodeError) as e:
                print(f"Error decoding JSON response for game ID {current_id} using endpoint {data_type}.")
                reset_http()
                backoff(data_type, current_id)
            
            except (ReadTimeout, ConnectTimeout) as e:
                print(f"{e} Error fetching {data_type} data for game ID {current_id}. Attempting to reset API and retry...")
                reset_http()
                backoff(data_type, current_id)
                
            df.to_csv(data_path, index=False)
            current_game_data += 1
            print(f"{data_type} {calculate_percent_completion(current_game_data,total_game_data)} complete!")

def reset_http():
    print("Savoir Reset")
    for adapter in requests.sessions.Session().adapters.values():
        adapter.close()

if __name__ == "__main__":
    for season in season_range(start_year, end_year): #Verifys players in season
        skeleton_save_path = f"{root}{season}/active_players.csv"
        log_save_path = f"{root}{season}/gamelog.csv"
        all_games_save_path = f"{root}{season}/all_games.csv"
        if not os.path.exists(f"{root}{season}"):
            Path(f"{root}{season}").mkdir(exist_ok=True, parents=True)
        if os.path.exists(skeleton_save_path) and os.path.exists(all_games_save_path) and os.path.exists(log_save_path):
            print(f"Season {season} data already exists.")
        else:
            if not os.path.exists(skeleton_save_path):
                df = LeagueDashPlayerStats(season=season,season_type_all_star="Regular Season").get_data_frames()[0]
                df['SEASON_ID'] = str(f"2{season}")[:5]
                df.to_csv(skeleton_save_path, index = False)
                print("players for season " + season + " created!")
            else:
                print(f"{season} players already exists\n")
            if not os.path.exists(all_games_save_path):
                df = LeagueGameFinder(season_nullable=season,player_or_team_abbreviation = "T", season_type_nullable="Regular Season").get_data_frames()[0]
                df.to_csv(all_games_save_path, index = False)
                print(season + " games created!")
            else:
                print(f"{season} games already exists\n")
            if not os.path.exists(log_save_path):
                df = PlayerGameLogs(season_nullable = season, season_type_nullable= 'Regular Season', timeout = 20).get_data_frames()[0]
                df.to_csv(log_save_path, index= False)
                print(season + " gamelog created!")
            else:
                print(f"{season} gamelog already exists\n")
    print("first testing connection\n")
    try:
        lebron_test = CommonPlayerInfo(player_id = 2544, timeout=5)
        df = lebron_test.get_data_frames()[0]
        print(f"\n{df}")
    except (ReadTimeout, ConnectTimeout):
        print("Could not print: The request timed out. The NBA server is likely busy.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    resume_id = input("\nType 'kill' to terminate ")
    if resume_id.lower() == "kill":
        sys.exit(1)

    for season in season_range(start_year, end_year):
        print(f"\n\n--------------------------\nNow working on season {season}")
        all_games_path = f"{root}{season}/all_games.csv"
        log_save_path = f"{root}{season}/gamelog.csv"
        
        
        creategameIDdata("playbyplay")
        creategameIDdata("advanced")
        creategameIDdata("defensive")
        creategameIDdata("fourfactors")
        creategameIDdata("hustle")


