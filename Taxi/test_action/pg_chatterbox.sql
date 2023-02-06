INSERT INTO chatterbox.supporter_tasks(supporter_login, task_id)
VALUES
('superuser', '5b2cae5cb2682a976914c2a1'),
('superuser', '5c2cae5cb2682a976914c2a1'),
('superuser', '5b2cae5cb4282a976914c2c9'),
('superuser', '5b2cae5cb2682a976914c2a2'),
('superuser', '5b2cae5cb2682a976914c2b0');

INSERT INTO chatterbox.online_supporters(supporter_login, status, lines, in_additional)
VALUES
('superuser', 'online', ARRAY['first'], false),
('user_with_in_additional_not_permitted', 'online', ARRAY['first'], true),
('user_with_off_shift_tickets_disabled', 'online', ARRAY['first'], true),
('test_user', 'online', ARRAY['first'], false);

INSERT INTO chatterbox.supporter_profile(
    supporter_login,
    in_additional_permitted
)
VALUES
('user_with_in_additional_not_permitted', false);

INSERT INTO chatterbox.supporter_profile(
    supporter_login,
    in_additional_permitted,
    off_shift_tickets_disabled,
    shift_start,
    shift_finish
)
VALUES
('user_with_off_shift_tickets_disabled', true, true, '2018-08-01T12:59:23.231000+00:00', '2018-08-01T15:59:23.231000+00:00');
