ALTER TABLE training_data ADD COLUMN days_since_last FLOAT;

WITH feature AS (
    SELECT 
        game_id,
        team_id,
        game_date,
        matchup,
        LEAST(
            10,
            COALESCE(
                DATEDIFF(
                    'day',
                    LAG(game_date) OVER (
                        PARTITION BY team_id
                        ORDER BY game_date
                    ),
                    game_date
                ),
                10
            )
        ) AS days_since_last
    FROM all_games
)

UPDATE training_data t
SET days_since_last = f.days_since_last
FROM feature f
WHERE t.game_id = f.game_id AND t.team_id = f.team_id
