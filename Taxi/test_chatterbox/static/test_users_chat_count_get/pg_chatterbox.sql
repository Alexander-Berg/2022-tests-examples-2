INSERT INTO chatterbox.online_supporters(supporter_login, status, lines)
VALUES
('user_1', 'before-break', ARRAY['first', 'second']),
('user_2', 'offline', ARRAY['first']),
('user_3', 'online', ARRAY['first', 'corp']),
('user_4', 'online-reversed', ARRAY['corp']),
('user_5', 'break', ARRAY['first']),
('user_6', 'training', ARRAY['second']),
('user_7', 'feedback', ARRAY['first', 'second']),
('user_8', 'technical_problems', ARRAY['corp']);

INSERT INTO chatterbox.supporter_tasks(supporter_login, task_id)
VALUES
('user_1', '5d398480779fb318087520d6'),
('user_1', '5b2cae5cb2682a976914c2a1'),
('user_2', '5d398480779fb31808752017'),
('user_3', '5b2cae5cb2682a976914c2a5');

INSERT INTO chatterbox.supporter_profile(supporter_login, max_chats)
VALUES
('user_1', 10),
('user_3', 2);
