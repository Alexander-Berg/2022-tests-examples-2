INSERT INTO chatterbox.supporter_profile(
    supporter_login,
    assigned_lines,
    can_choose_from_assigned_lines,
    can_choose_except_assigned_lines
)
VALUES
('user_with_default_values', ARRAY[]::TEXT[], FALSE, TRUE),
('user_with_custom_values', ARRAY['line_1', 'line_2'], TRUE, FALSE);
