ALTER TABLE training_data ADD COLUMN is_back_to_back FLOAT;
UPDATE training_data
SET is_back_to_back =
    CASE WHEN days_since_last = 1 THEN 1 ELSE 0 END; 