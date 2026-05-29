avg_opp_elo = True
is_home = True
days_since = True
is_back_to_back = True
games_played = True

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
            "ast", "tov", "stl", "blk", "pf", "plus_minus",
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
        "lat": 33.7573, "lon": -84.3963,
        "elevation_ft": 1026,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612738: {
        "arena": "TD Garden",
        "lat": 42.3662, "lon": -71.0621,
        "elevation_ft": 141,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612751: {
        "arena": "Barclays Center",
        "lat": 40.6826, "lon": -73.9754,
        "elevation_ft": 33,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612766: {
        "arena": "Spectrum Center",
        "lat": 35.2251, "lon": -80.8392,
        "elevation_ft": 748,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612741: {
        "arena": "United Center",
        "lat": 41.8807, "lon": -87.6742,
        "elevation_ft": 597,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612739: {
        "arena": "Rocket Mortgage FieldHouse",
        "lat": 41.4965, "lon": -81.6882,
        "elevation_ft": 653,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612765: {
        "arena": "Little Caesars Arena",
        "lat": 42.3410, "lon": -83.0550,
        "elevation_ft": 600,
        "tz": "America/Detroit", "utc_st": -5, "utc_dst": -4,
    },
    1610612754: {
        "arena": "Gainbridge Fieldhouse",
        "lat": 39.7639, "lon": -86.1555,
        "elevation_ft": 715,
        "tz": "America/Indiana/Indianapolis", "utc_st": -5, "utc_dst": -4,
    },
    1610612748: {
        "arena": "Kaseya Center",
        "lat": 25.7814, "lon": -80.1870,
        "elevation_ft": 6,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612749: {
        "arena": "Fiserv Forum",
        "lat": 43.0450, "lon": -87.9170,
        "elevation_ft": 617,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612752: {
        "arena": "Madison Square Garden",
        "lat": 40.7505, "lon": -73.9934,
        "elevation_ft": 33,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612753: {
        "arena": "Kia Center",
        "lat": 28.5392, "lon": -81.3839,
        "elevation_ft": 96,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612755: {
        "arena": "Wells Fargo Center",
        "lat": 39.9012, "lon": -75.1720,
        "elevation_ft": 39,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
    1610612761: {
        "arena": "Scotiabank Arena",
        "lat": 43.6435, "lon": -79.3791,
        "elevation_ft": 249,
        "tz": "America/Toronto", "utc_st": -5, "utc_dst": -4,
    },
    1610612764: {
        "arena": "Capital One Arena",
        "lat": 38.8981, "lon": -77.0209,
        "elevation_ft": 410,
        "tz": "America/New_York", "utc_st": -5, "utc_dst": -4,
    },
 
    # ── Western Conference ─────────────────────────────────────────
    1610612742: {
        "arena": "American Airlines Center",
        "lat": 32.7905, "lon": -96.8103,
        "elevation_ft": 430,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612743: {
        "arena": "Ball Arena",
        "lat": 39.7487, "lon": -105.0077,
        "elevation_ft": 5280,   # strongest elevation stressor in the NBA
        "tz": "America/Denver", "utc_st": -7, "utc_dst": -6,
    },
    1610612744: {
        "arena": "Chase Center",
        "lat": 37.7680, "lon": -122.3877,
        "elevation_ft": 20,
        "tz": "America/Los_Angeles", "utc_st": -8, "utc_dst": -7,
    },
    1610612745: {
        "arena": "Toyota Center",
        "lat": 29.7508, "lon": -95.3621,
        "elevation_ft": 43,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612746: {
        "arena": "Intuit Dome",
        "lat": 33.8430, "lon": -118.3617,
        "elevation_ft": 118,
        "tz": "America/Los_Angeles", "utc_st": -8, "utc_dst": -7,
    },
    1610612747: {
        "arena": "Crypto.com Arena",
        "lat": 34.0430, "lon": -118.2673,
        "elevation_ft": 285,
        "tz": "America/Los_Angeles", "utc_st": -8, "utc_dst": -7,
    },
    1610612763: {
        "arena": "FedExForum",
        "lat": 35.1382, "lon": -90.0505,
        "elevation_ft": 284,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612750: {
        "arena": "Target Center",
        "lat": 44.9795, "lon": -93.2760,
        "elevation_ft": 815,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612740: {
        "arena": "Smoothie King Center",
        "lat": 29.9490, "lon": -90.0812,
        "elevation_ft": 6,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612760: {
        "arena": "Paycom Center",
        "lat": 35.4634, "lon": -97.5151,
        "elevation_ft": 1201,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612756: {
        "arena": "Footprint Center",
        "lat": 33.4457, "lon": -112.0712,
        "elevation_ft": 1086,
        "tz": "America/Phoenix", "utc_st": -7, "utc_dst": -7,
    },
    1610612757: {
        "arena": "Moda Center",
        "lat": 45.5316, "lon": -122.6668,
        "elevation_ft": 50,
        "tz": "America/Los_Angeles", "utc_st": -8, "utc_dst": -7,
    },
    1610612758: {
        "arena": "Golden 1 Center",
        "lat": 38.5805, "lon": -121.4994,
        "elevation_ft": 30,
        "tz": "America/Los_Angeles", "utc_st": -8, "utc_dst": -7,
    },
    1610612759: {
        "arena": "Frost Bank Center",
        "lat": 29.4270, "lon": -98.4375,
        "elevation_ft": 650,
        "tz": "America/Chicago", "utc_st": -6, "utc_dst": -5,
    },
    1610612762: {
        "arena": "Delta Center",
        "lat": 40.7683, "lon": -111.9011,
        "elevation_ft": 4226,   # second-highest elevation stressor in the NBA
        "tz": "America/Denver", "utc_st": -7, "utc_dst": -6,
    },
}
