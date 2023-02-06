INSERT INTO chatterbox.supporter_profile(
    supporter_login,
    assigned_lines,
    can_choose_from_assigned_lines,
    can_choose_except_assigned_lines
)
VALUES
('user_1', ARRAY['line_1', 'line_2'], FALSE, FALSE),
('user_2', ARRAY['line_1', 'line_2'], FALSE, TRUE),
('user_3', ARRAY['line_1', 'line_2'], TRUE, FALSE);

INSERT INTO chatterbox.supporter_offer_skip_count(supporter_login, offer_skip_count)
VALUES
('user_1', 3),
('user_2', 3),
('user_3', 3);


