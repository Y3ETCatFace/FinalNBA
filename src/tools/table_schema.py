# =============================================================================
# CANONICAL SCHEMA PER TABLE
# =============================================================================
# After renaming, each table should contain exactly these columns.
# Any extra columns not in this set get dropped.
# Any missing columns get filled with None and flagged.

TABLE_SCHEMA = {
    "defensive" : {
        "whitelist": [
            "game_id", "team_id", "player_id",
            "matchup_minutes", "partial_possessions", "switches_on",
            "pts", "def_reb", "stl", "blk",
            "matchup_ast", "matchup_tov",
            "matchup_fgm", "matchup_fga", "matchup_fg_pct",
            "matchup_fg3m", "matchup_fg3a", "matchup_fg3_pct",
        ],
        "path": "defensive/*.csv",
    },    
    "all_games" : {
        "whitelist": [
            "game_id", "season_id", "game_date", "team_id", "team_abbrev",
            "team_name", "matchup", "win_loss", "minutes", "pts",
            "fgm", "fga", "fg_pct", "fg3m", "fg3a", "fg3_pct",
            "ftm", "fta", "ft_pct", "off_reb", "def_reb", "reb",
            "ast", "tov", "stl", "blk", "pf", "plus_minus",
        ],
        "path": "all_games.csv",
    },
    "advanced": {
        "whitelist": [
            "game_id", "team_id", "player_id", "minutes",
            "off_rating", "def_rating",
            "ast_pct", "ast_tov", "off_reb_pct", "def_reb_pct",
            "tov_ratio", "efg_pct", "ts_pct", "usage_pct",
            "pace",
        ],
        "path": "advanced/*.csv",
    },
    "fourfactors": {
        "whitelist": [
            "game_id", "team_id", "player_id", "minutes",
            "efg_pct", "ft_rate", "team_tov_pct", "off_reb_pct",
            "opp_efg_pct", "opp_ft_rate", "opp_tov_pct", "opp_off_reb_pct",
        ],
        "path": "fourfactors/*.csv",
    },
    "hustle": {
        "whitelist": [
            "game_id", "team_id", "player_id", "minutes", "pts",
            "contested_shots", "contested_shots_2pt", "contested_shots_3pt",
            "deflections", "charges_drawn", "screen_assists",
            "off_loose_balls_recovered", "def_loose_balls_recovered",
            "loose_balls_recovered", "off_boxouts", "def_boxouts",
            "boxout_team_rebs", "boxout_player_rebs", "box_outs",
        ],
        "path": "hustle/*.csv",
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
    "gamelog": {
        "whitelist": [
            "game_id", "season_id", "game_date", "player_id", "player_name",
            "team_id", "team_abbrev", "team_name", "matchup", "win_loss",
            "minutes", "pts", "fgm", "fga", "fg_pct",
            "fg3m", "fg3a", "fg3_pct", "ftm", "fta", "ft_pct",
            "off_reb", "def_reb", "reb", "ast", "tov", "stl",
            "blk", "blka", "pf", "pfd", "plus_minus",
            "double_doubles", "triple_doubles",
        ],
        "path": "gamelog.csv",
    },
    "active_players": {
        "whitelist": [
            "player_id", "player_name", "first_name", "last_name",
            "position", "team_id", "team_abbrev", "age",
            "games_played", "wins", "losses", "win_pct",
            "minutes", "pts", "ast", "reb", "stl", "blk",
            "tov", "fg_pct", "fg3_pct", "ft_pct", "plus_minus",
        ],
        "path": "active_players.csv",
    },
}