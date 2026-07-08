WITH fah AS(
    SELECT *,
    ROW_NUMBER() OVER(
        PARTITION BY game_id, player_id
        ORDER BY game_date
    ) AS rnk
) FROM gamelog
CREATE TABLE prime AS
SELECT * FROM fah
WHERE rnk <= 15