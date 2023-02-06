INSERT INTO chatterbox.supporter_profile(
    supporter_login,
    quality,
    languages,
    csat,
    is_piecework,
    updated,
    in_additional_permitted,
    off_shift_tickets_disabled
)
VALUES
('old_user_1', 0, ARRAY[]::VARCHAR(255)[], 0.0, false, '2018-01-01 00:00:00.000000+00', TRUE, TRUE),
('old_user_2', 0, ARRAY[]::VARCHAR(255)[], 0.0, false, '2018-01-01 00:00:00.000000+00', TRUE, TRUE);
