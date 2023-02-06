INSERT INTO chatterbox.supporter_profile(
    supporter_login,
    languages,
    is_piecework,
    updated,
    shift_start,
    shift_finish,
    max_tickets_per_shift
)
VALUES
('user_with_limit', ARRAY[]::VARCHAR(255)[], false, '2018-01-01 00:00:00.000000+00', '2018-01-01 12:00:00.000000+00', '2018-01-01 18:00:00.000000+00', 15),
('user_without_limit', ARRAY[]::VARCHAR(255)[], false, '2018-01-01 00:00:00.000000+00', NULL, NULL, NULL);
