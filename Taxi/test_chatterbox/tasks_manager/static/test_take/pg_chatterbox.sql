INSERT INTO chatterbox.supporter_profile(
    supporter_login,
    quality,
    languages,
    csat,
    is_piecework
)
VALUES
('user_with_ru_lang', 0, ARRAY['ru']::VARCHAR(255)[], 0.0, false),
('user_with_without_lang', 0, ARRAY[]::VARCHAR(255)[], 0.0, false),
('user_with_none_lang', 0, ARRAY[]::VARCHAR(255)[], 0.0, false);
