WITH reference as(
SELECT
game_id,
team_id,
AVG(minutes)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)
AS average_minutes,

AVG(pts)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)
AS average_points,

AVG(off_rating)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)
AS average_off_rating,

AVG(def_rating)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)
AS average_def_rating,

AVG(def_rating)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)
AS average_def_rating,

AVG(usage_pct)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)

AS average_usage_pct,

AVG(ts_pct)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)

AS average_ts_pct,

AVG(ast_pct)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)

AS average_ast_pct,

AVG(ast_tov)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)

AS average_ast_tov,

AVG(off_reb_pct)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)

AS average_off_reb_pct,

AVG(def_reb_pct)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)

AS average_def_reb_pct,

AVG(tov_ratio)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)

AS average_tov_ratio,

AVG(ft_rate)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)

AS average_ft_rate,

AVG(efg_pct)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)

AS average_efg_pct,

AVG(stl)
OVER (PARTITION BY player_id 
    ORDER BY game_date
    ROWS BETWEEN 15 
    PRECEDING AND 1 PRECEDING)
AS average_stl,

FROM
master_nba
),


random as (
SELECT 
    *,
    ROW_NUMBER() OVER (PARTITION BY game_id, team_id ORDER BY average_minutes DESC) AS rnk
FROM
    reference
)

SELECT
    *
FROM
    random
WHERE rnk <= 9
ORDER BY team_id, game_id, rnk

