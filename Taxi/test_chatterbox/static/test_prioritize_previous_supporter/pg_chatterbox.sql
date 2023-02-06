INSERT INTO chatterbox.online_supporters(supporter_login, status, lines)
VALUES
('user_1', 'online', ARRAY['eda_tips', 'eda_first']),
('user_2', 'online', ARRAY['eda_first']),
('user_3', 'online', ARRAY['eda_first']),
('user_4', 'online', ARRAY['eda_tips']);

INSERT INTO chatterbox.supporter_profile(supporter_login, max_chats, is_piecework)
VALUES
('user_1', 2, TRUE),
('user_2', 2, TRUE),
('user_3', 2, FALSE),
('user_4', 2, FALSE);

INSERT INTO chatterbox.supporter_tasks(supporter_login, task_id)
VALUES
('user_1', '5b2cae5cb2682a976914c2a0'),
('user_2', '5b2cae5cb2682a976914c2a1'),
('user_2', '5b2cae5cb2682a976914c2a2');
