# =============================================================================
# CANONICAL SCHEMA PER TABLE
# =============================================================================
# After renaming, each table should contain exactly these columns.
# Any extra columns not in this set get dropped.
# Any missing columns get filled with None and flagged.

TABLE_SCHEMA = {

    "games": [
        "game_id", "season_id", "game_date", "team_id", "team_abbrev",
        "team_name", "matchup", "win_loss", "minutes", "pts",
        "fgm", "fga", "fg_pct", "fg3m", "fg3a", "fg3_pct",
        "ftm", "fta", "ft_pct", "off_reb", "def_reb", "reb",
        "ast", "tov", "stl", "blk", "pf", "plus_minus",
    ],

    "advanced": [
        "game_id", "team_id", "player_id", "minutes",
        "off_rating", "def_rating", "net_rating",
        "est_off_rating", "est_def_rating", "est_net_rating",
        "ast_pct", "ast_tov", "off_reb_pct", "def_reb_pct",
        "tov_ratio", "efg_pct", "ts_pct", "usage_pct",
        "pace", "possessions", "pie",
    ],

    "four_factors": [
        "game_id", "team_id", "player_id", "minutes",
        "efg_pct", "ft_rate", "team_tov_pct", "off_reb_pct",
        "opp_efg_pct", "opp_ft_rate", "opp_tov_pct", "opp_off_reb_pct",
    ],

    "hustle": [
        "game_id", "team_id", "player_id", "minutes", "pts",
        "contested_shots", "contested_shots_2pt", "contested_shots_3pt",
        "deflections", "charges_drawn", "screen_assists",
        "off_loose_balls_recovered", "def_loose_balls_recovered",
        "loose_balls_recovered", "off_boxouts", "def_boxouts",
        "boxout_team_rebs", "boxout_player_rebs", "box_outs",
    ],

    "play_by_play": [
        "game_id", "action_id", "action_number", "period", "clock",
        "team_id", "team_abbrev", "player_id", "player_name",
        "x_coord", "y_coord", "shot_distance", "shot_result",
        "is_field_goal", "shot_value", "score_home", "score_away",
        "points_total", "location", "action_type", "sub_type", "description",
        "video_available",
    ],

    "gamelog": [
        "game_id", "season_id", "game_date", "player_id", "player_name",
        "team_id", "team_abbrev", "team_name", "matchup", "win_loss",
        "minutes", "pts", "fgm", "fga", "fg_pct",
        "fg3m", "fg3a", "fg3_pct", "ftm", "fta", "ft_pct",
        "off_reb", "def_reb", "reb", "ast", "tov", "stl",
        "blk", "blka", "pf", "pfd", "plus_minus",
        "double_doubles", "triple_doubles",
    ],

    "players": [
        "player_id", "player_name", "first_name", "last_name",
        "position", "team_id", "team_abbrev", "age",
        "games_played", "wins", "losses", "win_pct",
        "minutes", "pts", "ast", "reb", "stl", "blk",
        "tov", "fg_pct", "fg3_pct", "ft_pct", "plus_minus",
    ],

    # Computed — not loaded from source
    "elo_daily": [
        "date", "team_id", "elo",
    ],
}
