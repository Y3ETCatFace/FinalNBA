import pandas as pd
def sql_script(path):
    with open(path) as sql:
        return sql.read()
    
def clean_data(col, data_type):
    whitelist = TABLE_SCHEMA[data_type]['whitelist']
    filter = {f: s for f, s in MASTER_MAP.items() if f in col and (s in whitelist)}
    master_string = f'{", ".join(f"{f} as {s}" for f, s in filter.items())}'
    return master_string

def clean_df(df, data_type):
    whitelist = TABLE_SCHEMA[data_type]['whitelist']
    filter = {f: s for f, s in MASTER_MAP.items() if f in df.columns and (s in whitelist)}
    print(f'whitelist is {whitelist}')
    return df.reindex(columns = filter.keys()).rename(columns = filter)

def create_elo(df):
    id_elo = {}
    id_season_id = {}
    df['elo'] = pd.NA
    for i in range(0, len(df), 2):
        id_a = df.iloc[i]['team_id']
        id_b = df.iloc[i+1]['team_id']
        outcome_a = df.iloc[i]['outcome']
        outcome_b = df.iloc[i+1]['outcome']
        new_a_season_id = df.iloc[i]['season_id']
        new_b_season_id = df.iloc[i+1]['season_id']
        a_season_id = id_season_id.get(id_a, None)
        b_season_id = id_season_id.get(id_b, None)
        a_elo = id_elo.get(id_a, 1500)
        b_elo = id_elo.get(id_b, 1500)
        outcome = 1 if outcome_a > outcome_b else 0
        if new_a_season_id != a_season_id:
            a_season_game_count = 1
        elif a_season_game_count < 5:
            a_season_game_count += 1
        if new_b_season_id != b_season_id:
            b_season_game_count = 1
        elif b_season_game_count < 5:
            b_season_game_count += 1
        new_a_elo, new_b_elo = calculate_elo(a_elo, b_elo, outcome, new_a_season_id, new_b_season_id, a_season_id, b_season_id, a_season_game_count, b_season_game_count) #Outcome 1 means team A won
        df.at[i, 'elo'] = new_a_elo
        df.at[i+1, 'elo'] = new_b_elo
        id_elo[id_a] = new_a_elo
        id_elo[id_b] = new_b_elo
        id_season_id[id_a] = new_a_season_id
        id_season_id[id_b] = new_b_season_id
    df.drop(columns=['season_id'], inplace=True) #-------------------------------------------
    return df

def calculate_elo(elo_a, elo_b, outcome, 
        a_season_id, b_season_id, 
        a_last_season_id, b_last_season_id,
        a_season_game_count, b_season_game_count,
        roster_continuity_a=1.0, roster_continuity_b=1.0, 
                k=20):
    if a_season_id != a_last_season_id:
        elo_a = elo_a + (1500 - elo_a) * (1 - roster_continuity_a)
        k_a = k * (1 + max(0, (5 - a_season_game_count) / 5))
    else:
        k_a = k
    if b_season_id != b_last_season_id:
        elo_b = elo_b + (1500 - elo_b) * (1 - roster_continuity_b)
        k_b = k * (1 + max(0, (5 - b_season_game_count) / 5))
    else:
        k_b = k
    expected = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    new_elo_a = elo_a + k_a * (outcome - expected)
    new_elo_b = elo_b + k_b * ((1 - outcome) - (1 - expected))
    return new_elo_a, new_elo_b

def get_connection():
    import os
    from pathlib import Path
    import duckdb
    db_path = "data/nba.db"
    if not os.path.exists(db_path):
        Path(db_path).parent.mkdir(exist_ok=True, parents=True)
    return duckdb.connect(db_path)

TABLE_SCHEMA = {
    # ── JOINED TABLES ──────────────────────────────────────────────
    "gamelog": {
        "whitelist": [
            "game_id", "season_id", "game_date",
            "player_id", "player_name",
            "team_id", "team_abbrev", "team_name",
            "matchup", "win_loss",
            "minutes", "pts",
            "fgm", "fga", "fg_pct",
            "fg3m", "fg3a", "fg3_pct",
            "ftm", "fta", "ft_pct",
            "off_reb", "def_reb", "reb",
            "ast", "tov", "stl", "blk", "blka",
            "pf", "pfd", "plus_minus",
            "double_doubles", "triple_doubles",
        ], 
        "path": "gamelog.csv",
    },
    "advanced": {
        "whitelist": [
            "game_id", "player_id",
            # minutes removed — in gamelog
            "off_rating", "def_rating",
            "ast_pct", "ast_tov",
            "off_reb_pct", "def_reb_pct",
            "tov_ratio", "efg_pct",
            "ts_pct", "usage_pct", "pace",
        ],
        "path": "advanced/*.csv",
    },
    "defensive": {
        "whitelist": [
            "game_id", "player_id",
            "pts_allowed",
            "matchup_minutes", "partial_possessions", "switches_on",
            "matchup_ast", "matchup_tov",
            "matchup_fgm", "matchup_fga", "matchup_fg_pct",
            "matchup_fg3m", "matchup_fg3a", "matchup_fg3_pct",
        ],
        "path": "defensive/*.csv",
    },
    "fourfactors": {
        "whitelist": [
            "game_id", "player_id",
            # minutes, efg_pct, off_reb_pct removed — in gamelog/advanced
            "ft_rate", "team_tov_pct",
            "opp_efg_pct", "opp_ft_rate", "opp_tov_pct", "opp_off_reb_pct",
        ],
        "path": "fourfactors/*.csv",
    },
    "hustle": {
        "whitelist": [
            "game_id",  "player_id",
            # minutes, pts removed — in gamelog
            "contested_shots", "contested_shots_2pt", "contested_shots_3pt",
            "deflections", "charges_drawn", "screen_assists",
            "off_loose_balls_recovered", "def_loose_balls_recovered",
            "loose_balls_recovered", "off_boxouts", "def_boxouts",
            "boxout_team_rebs", "boxout_player_rebs", "box_outs",
        ],
        "path": "hustle/*.csv",
    },

    # ── BONUS TABLES (standalone, not joined) ──────────────────────
    "all_games": {
        "whitelist": [
            "game_id", "season_id", "game_date", "team_id", "team_abbrev",
            "team_name", "matchup", "win_loss", "minutes", "pts",
            "fgm", "fga", "fg_pct", "fg3m", "fg3a", "fg3_pct",
            "ftm", "fta", "ft_pct", "off_reb", "def_reb", "reb",
            "ast", "tov", "stl", "blk", "pf", "plus_minus", 'opponent_id'
        ],
        "path": "all_games.csv",
    },
    "play_by_play": {
        "whitelist": [
            "game_id", "action_id", "action_number", "period", "clock",
            "team_id", "team_abbrev", "player_id", "player_name",
            "x_coord", "y_coord", "shot_distance", "shot_result",
            "is_field_goal", "shot_value", "score_home", "score_away",
            "points_total", "location", "action_type", "sub_type", "description",
        ],
        "path": "playbyplay/*.csv",
    },
    "active_players": {
        "whitelist": [
            "player_id", "player_name", "season_id", "first_name", "last_name",
            "position", "team_id", "team_abbrev", "age",
            "games_played", "wins", "losses", "win_pct",
            "minutes", "pts", "ast", "reb", "stl", "blk",
            "tov", "fg_pct", "fg3_pct", "ft_pct", "plus_minus",
        ],
        "path": "active_players.csv",
    },
    "biometrics" : {
        "whitelist": [
            'height', 'weight', 'season_exp', 'school', 'player_name'
        ],
        'path': 'biometrics.csv'
    }
}
# =============================================================================
# NBA DATA HEADER NORMALIZATION REGISTRY
# =============================================================================
# Maps every raw source column name → canonical internal schema name
# Usage:
#   df.rename(columns=MASTER_MAP, inplace=True)
#   df = df[[c for c in df.columns if c in KEEP_COLUMNS]]
# =============================================================================
MASTER_MAP = {

    # -------------------------------------------------------------------------
    # IDENTIFIERS
    # -------------------------------------------------------------------------
    "DISPLAY_FIRST_LAST":   "player_name",
    "SCHOOL":               "school",
    'SEASON_EXP':           "season_exp",
    "HEIGHT":               'height',
    'WEIGHT':               "weight",
    "gameId":               "game_id",
    "GAME_ID":              "game_id",
    "teamId":               "team_id",
    "TEAM_ID":              "team_id",
    "personId":             "player_id",
    "PLAYER_ID":            "player_id",
    "SEASON_ID":            "season_id",
    "SEASON_YEAR":          "season_id",

    # -------------------------------------------------------------------------
    # PLAYER INFO
    # -------------------------------------------------------------------------
    "firstName":            "first_name",
    "familyName":           "last_name",
    "PLAYER_NAME":          "player_name",
    "playerName":           "player_name",
    "nameI":                "name_initial",
    "playerNameI":          "name_initial",
    "NICKNAME":             "nickname",
    "playerSlug":           "player_slug",
    "position":             "position",
    "START_POSITION":       "position",
    "jerseyNum":            "jersey_num",
    "comment":              "comment",
    "COMMENT":              "comment",
    "AGE":                  "age",

    # -------------------------------------------------------------------------
    # TEAM INFO
    # -------------------------------------------------------------------------
    "teamCity":             "team_city",
    "TEAM_CITY":            "team_city",
    "teamName":             "team_name",
    "TEAM_NAME":            "team_name",
    "teamTricode":          "team_abbrev",
    "TEAM_ABBREVIATION":    "team_abbrev",
    "teamSlug":             "team_slug",

    # -------------------------------------------------------------------------
    # GAME INFO
    # -------------------------------------------------------------------------
    "GAME_DATE":            "game_date",
    "MATCHUP":              "matchup",
    "WL":                   "win_loss",
    "TEAM_COUNT":           "team_count",
    "AVAILABLE_FLAG":       "available_flag",

    # -------------------------------------------------------------------------
    # MINUTES
    # -------------------------------------------------------------------------
    "minutes":              "minutes",
    "MIN":                  "minutes",
    "MINUTES":              "minutes",
    "MIN_SEC":              "minutes_sec",        # MM:SS string, parse separately

    # -------------------------------------------------------------------------
    # BASE BOX SCORE STATS
    # -------------------------------------------------------------------------
    "PTS":                  "pts",
    "pts":                  "pts",
    "playerPoints":         "pts_allowed",
    "FGM":                  "fgm",
    "FGA":                  "fga",
    "FG_PCT":               "fg_pct",
    "FG3M":                 "fg3m",
    "FG3A":                 "fg3a",
    "FG3_PCT":              "fg3_pct",
    "FTM":                  "ftm",
    "FTA":                  "fta",
    "FT_PCT":               "ft_pct",
    "OREB":                 "off_reb",
    "DREB":                 "def_reb",
    "defensiveRebounds":    "def_reb",
    "REB":                  "reb",
    "AST":                  "ast",
    "TOV":                  "tov",
    "STL":                  "stl",
    "steals":               "stl",
    "BLK":                  "blk",
    "blocks":               "blk",
    "BLKA":                 "blka",
    "PF":                   "pf",
    "PFD":                  "pfd",
    "PLUS_MINUS":           "plus_minus",

    # -------------------------------------------------------------------------
    # SEASON AGGREGATE (active_players / gamelog)
    # -------------------------------------------------------------------------
    "GP":                   "games_played",
    "W":                    "wins",
    "L":                    "losses",
    "W_PCT":                "win_pct",
    "DD2":                  "double_doubles",
    "TD3":                  "triple_doubles",
    "NBA_FANTASY_PTS":      "nba_fantasy_pts",
    "WNBA_FANTASY_PTS":     "wnba_fantasy_pts",

    # -------------------------------------------------------------------------
    # ADVANCED STATS
    # -------------------------------------------------------------------------
    "offensiveRating":              "off_rating",
    "estimatedOffensiveRating":     "est_off_rating",
    "defensiveRating":              "def_rating",
    "estimatedDefensiveRating":     "est_def_rating",
    "netRating":                    "net_rating",
    "estimatedNetRating":           "est_net_rating",
    "assistPercentage":             "ast_pct",
    "assistToTurnover":             "ast_tov",
    "assistRatio":                  "ast_ratio",
    "offensiveReboundPercentage":   "off_reb_pct",
    "defensiveReboundPercentage":   "def_reb_pct",
    "reboundPercentage":            "reb_pct",
    "turnoverRatio":                "tov_ratio",
    "effectiveFieldGoalPercentage": "efg_pct",
    "trueShootingPercentage":       "ts_pct",
    "usagePercentage":              "usage_pct",
    "estimatedUsagePercentage":     "est_usage_pct",
    "estimatedPace":                "est_pace",
    "pace":                         "pace",
    "pacePer40":                    "pace_per40",
    "possessions":                  "possessions",
    "PIE":                          "pie",

    # -------------------------------------------------------------------------
    # FOUR FACTORS
    # -------------------------------------------------------------------------
    "freeThrowAttemptRate":             "ft_rate",
    "teamTurnoverPercentage":           "team_tov_pct",
    "oppEffectiveFieldGoalPercentage":  "opp_efg_pct",
    "oppFreeThrowAttemptRate":          "opp_ft_rate",
    "oppTeamTurnoverPercentage":        "opp_tov_pct",
    "oppOffensiveReboundPercentage":    "opp_off_reb_pct",

    # -------------------------------------------------------------------------
    # HUSTLE STATS
    # -------------------------------------------------------------------------
    "CONTESTED_SHOTS":              "contested_shots",
    "CONTESTED_SHOTS_2PT":          "contested_shots_2pt",
    "CONTESTED_SHOTS_3PT":          "contested_shots_3pt",
    "DEFLECTIONS":                  "deflections",
    "CHARGES_DRAWN":                "charges_drawn",
    "SCREEN_ASSISTS":               "screen_assists",
    "SCREEN_AST_PTS":               "screen_ast_pts",
    "OFF_LOOSE_BALLS_RECOVERED":    "off_loose_balls_recovered",
    "DEF_LOOSE_BALLS_RECOVERED":    "def_loose_balls_recovered",
    "LOOSE_BALLS_RECOVERED":        "loose_balls_recovered",
    "OFF_BOXOUTS":                  "off_boxouts",
    "DEF_BOXOUTS":                  "def_boxouts",
    "BOX_OUT_PLAYER_TEAM_REBS":     "boxout_team_rebs",
    "BOX_OUT_PLAYER_REBS":          "boxout_player_rebs",
    "BOX_OUTS":                     "box_outs",

    # -------------------------------------------------------------------------
    # DEFENSIVE MATCHUP STATS
    # -------------------------------------------------------------------------
    "matchupMinutes":               "matchup_minutes",
    "partialPossessions":           "partial_possessions",
    "switchesOn":                   "switches_on",
    "matchupAssists":               "matchup_ast",
    "matchupTurnovers":             "matchup_tov",
    "matchupFieldGoalsMade":        "matchup_fgm",
    "matchupFieldGoalsAttempted":   "matchup_fga",
    "matchupFieldGoalPercentage":   "matchup_fg_pct",
    "matchupThreePointersMade":     "matchup_fg3m",
    "matchupThreePointersAttempted":"matchup_fg3a",
    "matchupThreePointerPercentage":"matchup_fg3_pct",

    # -------------------------------------------------------------------------
    # PLAY-BY-PLAY
    # -------------------------------------------------------------------------
    "actionNumber":         "action_number",
    "clock":                "clock",
    "period":               "period",
    "xLegacy":              "x_coord",
    "yLegacy":              "y_coord",
    "shotDistance":         "shot_distance",
    "shotResult":           "shot_result",
    "isFieldGoal":          "is_field_goal",
    "scoreHome":            "score_home",
    "scoreAway":            "score_away",
    "pointsTotal":          "points_total",
    "location":             "location",
    "description":          "description",
    "actionType":           "action_type",
    "subType":              "sub_type",
    "videoAvailable":       "video_available",
    "shotValue":            "shot_value",
    "actionId":             "action_id",
}

geo = {
    # ── Eastern Conference ─────────────────────────────────────────
    1610612737: {
        "arena": "State Farm Arena",
        "coords": (33.7573, -84.3963),
        "elevation_ft": 1026,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612738: {
        "arena": "TD Garden",
        "coords": (42.3662, -71.0621),
        "elevation_ft": 141,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612751: {
        "arena": "Barclays Center",
        "coords": (40.6826, -73.9754),
        "elevation_ft": 33,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612766: {
        "arena": "Spectrum Center",
        "coords": (35.2251, -80.8392),
        "elevation_ft": 748,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612741: {
        "arena": "United Center",
        "coords": (41.8807, -87.6742),
        "elevation_ft": 597,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612739: {
        "arena": "Rocket Mortgage FieldHouse",
        "coords": (41.4965, -81.6882),
        "elevation_ft": 653,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612765: {
        "arena": "Little Caesars Arena",
        "coords": (42.3410, -83.0550),
        "elevation_ft": 600,
        "tz": "America/Detroit", "utc_st": -5, "utc_dst": -4,
    },
    1610612754: {
        "arena": "Gainbridge Fieldhouse",
        "coords": (39.7639, -86.1555),
        "elevation_ft": 715,
        "tz": "America/Indiana/Indianapolis", "utc_st": -5, "utc_dst": -4,
    },
    1610612748: {
        "arena": "Kaseya Center",
        "coords": (25.7814, -80.1870),
        "elevation_ft": 6,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612749: {
        "arena": "Fiserv Forum",
        "coords": (43.0450, -87.9170),
        "elevation_ft": 617,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612752: {
        "arena": "Madison Square Garden",
        "coords": (40.7505, -73.9934),
        "elevation_ft": 33,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612753: {
        "arena": "Kia Center",
        "coords": (28.5392, -81.3839),
        "elevation_ft": 96,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612755: {
        "arena": "Wells Fargo Center",
        "coords": (39.9012, -75.1720),
        "elevation_ft": 39,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612761: {
        "arena": "Scotiabank Arena",
        "coords": (43.6435, -79.3791),
        "elevation_ft": 249,
        "tz": "America/Toronto", "utc_st": -5, "utc_dst": -4,
    },
    1610612764: {
        "arena": "Capital One Arena",
        "coords": (38.8981, -77.0209),
        "elevation_ft": 410,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },

    # ── Western Conference ─────────────────────────────────────────
    1610612742: {
        "arena": "American Airlines Center",
        "coords": (32.7905, -96.8103),
        "elevation_ft": 430,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612743: {
        "arena": "Ball Arena",
        "coords": (39.7487, -105.0077),
        "elevation_ft": 5280,
        "tz": "America/Denver", "utc_st": -7, "utc_dst": -6,
    },
    1610612744: {
        "arena": "Chase Center",
        "coords": (37.7680, -122.3877),
        "elevation_ft": 20,
        "tz": "America/Los_Angeles", "utc_st": -8, "utc_dst": -7,
    },
    1610612745: {
        "arena": "Toyota Center",
        "coords": (29.7508, -95.3621),
        "elevation_ft": 43,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612746: {
        "arena": "Intuit Dome",
        "coords": (33.8430, -118.3617),
        "elevation_ft": 118,
        "tz": "America/Los_Angeles", "utc_st": -8, "utc_dst": -7,
    },
    1610612747: {
        "arena": "Crypto.com Arena",
        "coords": (34.0430, -118.2673),
        "elevation_ft": 285,
        "tz": "America/Los_Angeles", "utc_st": -8, "utc_dst": -7,
    },
    1610612763: {
        "arena": "FedExForum",
        "coords": (35.1382, -90.0505),
        "elevation_ft": 284,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612750: {
        "arena": "Target Center",
        "coords": (44.9795, -93.2760),
        "elevation_ft": 815,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612740: {
        "arena": "Smoothie King Center",
        "coords": (29.9490, -90.0812),
        "elevation_ft": 6,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612760: {
        "arena": "Paycom Center",
        "coords": (35.4634, -97.5151),
        "elevation_ft": 1201,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612756: {
        "arena": "Footprint Center",
        "coords": (33.4457, -112.0712),
        "elevation_ft": 1086,
        "tz": "America/Phoenix", "utc_st": -7, "utc_dst": -7,
    },
    1610612757: {
        "arena": "Moda Center",
        "coords": (45.5316, -122.6668),
        "elevation_ft": 50,
        "tz": "America/Los_Angeles", "utc_st": -8, "utc_dst": -7,
    },
    1610612758: {
        "arena": "Golden 1 Center",
        "coords": (38.5805, -121.4994),
        "elevation_ft": 30,
        "tz": "America/Los_Angeles", "utc_st": -8, "utc_dst": -7,
    },
    1610612759: {
        "arena": "Frost Bank Center",
        "coords": (29.4270, -98.4375),
        "elevation_ft": 650,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612762: {
        "arena": "Delta Center",
        "coords": (40.7683, -111.9011),
        "elevation_ft": 4226,
        "tz": "America/Denver", "utc_st": -7, "utc_dst": -6,
    },
}

nba_team_map = {
    # ATLANTA HAWKS
    "ATLANTA HAWKS": "ATL",
    
    # BOSTON CELTICS
    "BOSTON CELTICS": "BOS",
    
    # BROOKLYN NETS
    "BROOKLYN NETS": "BKN",
    
    # CHARLOTTE HORNETS
    "CHARLOTTE HORNETS": "CHA",
    
    # CHICAGO BULLS
    "CHICAGO BULLS": "CHI",
    
    # CLEVELAND CAVALIERS
    "CLEVELAND CAVALIERS": "CLE",
    
    # DALLAS MAVERICKS
    "DALLAS MAVERICKS": "DAL",
    
    # DENVER NUGGETS
    "DENVER NUGGETS": "DEN",
    
    # DETROIT PISTONS
    "DETROIT PISTONS": "DET",
    
    # GOLDEN STATE WARRIORS
    "GOLDEN STATE WARRIORS": "GSW",
    
    # HOUSTON ROCKETS
    "HOUSTON ROCKETS": "HOU",
    
    # INDIANA PACERS
    "INDIANA PACERS": "IND",
    
    # LOS ANGELES CLIPPERS
    "LOS ANGELES CLIPPERS": "LAC",
    "LA CLIPPERS": "LAC",  # Model safety backup
    
    # LOS ANGELES LAKERS
    "LOS ANGELES LAKERS": "LAL",
    
    # MEMPHIS GRIZZLIES
    "MEMPHIS GRIZZLIES": "MEM",
    
    # MIAMI HEAT
    "MIAMI HEAT": "MIA",
    
    # MILWAUKEE BUCKS
    "MILWAUKEE BUCKS": "MIL",
    
    # MINNESOTA TIMBERWOLVES
    "MINNESOTA TIMBERWOLVES": "MIN",
    
    # NEW ORLEANS PELICANS
    "NEW ORLEANS PELICANS": "NOP",
    
    # NEW YORK KNICKS
    "NEW YORK KNICKS": "NYK",
    
    # OKLAHOMA CITY THUNDER
    "OKLAHOMA CITY THUNDER": "OKC",
    
    # ORLANDO MAGIC
    "ORLANDO MAGIC": "ORL",
    
    # PHILADELPHIA 76ERS
    "PHILADELPHIA 76ERS": "PHI",
    
    # PHOENIX SUNS
    "PHOENIX SUNS": "PHX",
    
    # PORTLAND TRAIL BLAZERS
    "PORTLAND TRAIL BLAZERS": "POR",
    
    # SACRAMENTO KINGS
    "SACRAMENTO KINGS": "SAC",
    
    # SAN ANTONIO SPURS
    "SAN ANTONIO SPURS": "SAS",
    
    # TORONTO RAPTORS
    "TORONTO RAPTORS": "TOR",
    
    # UTAH JAZZ
    "UTAH JAZZ": "UTA",
    
    # WASHINGTON WIZARDS
    "WASHINGTON WIZARDS": "WAS"
}
important_series = {
    'next_team': 'kxnextteamnba'
}