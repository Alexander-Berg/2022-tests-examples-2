INSERT INTO chatterbox.online_supporters(supporter_login, status, lines, last_action_ts, in_additional, updated)
VALUES
('user_1', 'online', ARRAY['first'], '2019-08-13 11:49:25.000000+00', false, '2019-08-13 11:49:25.000000+00'),
('user_2', 'online', ARRAY['first', 'new'], '2019-08-13 11:49:25.000000+00', true, '2019-08-13 11:49:25.000000+00'),
('user_3', 'online', ARRAY['second'], '2019-08-13 11:51:25.000000+00', false, '2019-08-13 11:50:25.000000+00'),
('user_4', 'online', ARRAY['first'], '2019-08-13 11:51:25.000000+00', true, '2019-08-13 11:49:25.000000+00'),
('user_5', 'offline', ARRAY['first', 'second'], '2019-08-13 11:51:25.000000+00', false, '2019-08-13 11:49:25.000000+00'),
('user_6', 'offline', ARRAY['second'], '2019-08-13 11:51:25.000000+00', true, '2019-08-13 11:50:55.000000+00'),
('user_7', 'offline', ARRAY['first'], '2019-08-13 11:49:25.000000+00', true, '2019-08-13 11:49:25.000000+00'),
('user_8', 'before-break', ARRAY['first'], '2019-08-13 11:49:25.000000+00', false, '2019-08-13 11:49:25.000000+00');
