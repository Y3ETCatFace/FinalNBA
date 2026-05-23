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
