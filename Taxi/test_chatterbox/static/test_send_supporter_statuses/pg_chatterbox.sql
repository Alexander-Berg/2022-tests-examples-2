INSERT INTO chatterbox.online_supporters(supporter_login, status, lines, in_additional, updated)
VALUES
('user_1', 'online', ARRAY['first'], false, '2019-08-13 11:49:25.000000+00'),
('user_2', 'online', ARRAY['first', 'second'], true, '2019-08-12 23:55:00.000000+00'),
('user_3', 'offline', ARRAY['first'], false, '2019-08-13 10:00:00.000000+00');
