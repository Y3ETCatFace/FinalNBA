ALTER TABLE training_data ADD COLUMN games_played FLOAT;

WITH games_played_feature AS (
SELECT
ROW_NUMBER()
OVER(PARTITION BY team_id, season_id ORDER BY game_date) as games_played,
team_id,
game_id
FROM all_games 
)

UPDATE training_data t
SET games_played = f.games_played
FROM games_played_feature f
WHERE t.team_id = f.team_id AND t.game_id = f.game_id
