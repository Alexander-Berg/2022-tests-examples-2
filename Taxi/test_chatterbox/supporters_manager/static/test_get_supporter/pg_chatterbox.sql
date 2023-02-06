INSERT INTO chatterbox.online_supporters(
    supporter_login,
    status,
    lines,
    last_action_ts,
    in_additional,
    updated
)
VALUES
('user_with_status_and_profile', 'online', ARRAY['first'], '2019-01-01 00:00:00.000000+00', false, '2019-01-01 00:00:00.000000+00'),
('user_with_status_and_without_profile', 'online', ARRAY['first', 'new'], '2019-01-01 00:00:00.000000+00', true, '2019-01-01 00:00:00.000000+00');

INSERT INTO chatterbox.supporter_profile(
    supporter_login,
    languages,
    max_tickets_per_shift,
    shift_start,
    shift_finish,
    in_additional_permitted,
    off_shift_tickets_disabled
)
VALUES
('user_without_status_and_with_profile', '{"ru"}', 10, '2019-01-01 00:00:00.000000+00', '2019-01-02 00:00:00.000000+00', FALSE, TRUE),
('user_with_status_and_profile', '{"en"}', NULL, NULL, NULL, NULL, NULL);
