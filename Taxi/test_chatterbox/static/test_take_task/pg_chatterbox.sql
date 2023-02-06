INSERT INTO chatterbox.online_supporters(supporter_login, status, lines, in_additional)
VALUES
('superuser', 'online', ARRAY['first'], false),
('user_with_in_additional_not_permitted', 'online', ARRAY['first'], true),
('user_with_in_additional_not_permitted_task_assigned', 'online', ARRAY['first'], true);

INSERT INTO chatterbox.supporter_profile(
    supporter_login,
    quality,
    languages,
    csat,
    is_piecework,
    updated,
    in_additional_permitted
)
VALUES
('superuser2', 0, '{"en", "ru"}', 0.0, false, '2018-01-01 00:00:00.000000+00', true),
('user_with_in_additional_not_permitted', 0, '{"en", "ru"}', 0.0, false, '2018-01-01 00:00:00.000000+00', false),
('user_with_in_additional_not_permitted_task_assigned', 0, '{"en", "ru"}', 0.0, false, '2018-01-01 00:00:00.000000+00', false);

INSERT INTO chatterbox.supporter_profile(
    supporter_login,
    in_additional_permitted,
    off_shift_tickets_disabled,
    shift_start,
    shift_finish
)
VALUES
('user_with_off_shift_tickets_disabled', true, true, '2018-08-01T12:59:23.231000+00:00', '2018-08-01T15:59:23.231000+00:00');
