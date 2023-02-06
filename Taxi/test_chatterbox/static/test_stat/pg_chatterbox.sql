INSERT INTO chatterbox.online_supporters(supporter_login, status, lines)
VALUES
('user_1', 'online', ARRAY['first', 'second']),
('user_2', 'offline', ARRAY['first', 'second']),
('user_3', 'online', ARRAY['second']),
('user_4', 'online', ARRAY['first']),
('user_5', 'online', ARRAY['corp']),
('user_6', 'online', ARRAY['corp']),
('user_7', 'online', ARRAY['corp']),
('user_8', 'offline', ARRAY['corp', 'new_line']),
('user_9', 'online', ARRAY['vip', 'corp']),
('user_10', 'online', ARRAY['hard_line']),
('user_11', 'online-reversed', ARRAY['corp']),
('user_12', 'online-in-additional', ARRAY['first']),
('user_13', 'online-reversed-in-additional', ARRAY['first']),
('user_14', 'online', ARRAY['telephony_line']),
('user_15', 'online', ARRAY['telephony_line']),
('user_16', 'online-in-additional', ARRAY['telephony_line']),
('user_17', 'offline', ARRAY['telephony_line']),
('user_18', 'online', ARRAY['telephony_line_second']),
('user_19', 'online', ARRAY['telephony_line_second']);


INSERT INTO chatterbox.supporter_tasks(supporter_login, task_id)
VALUES
('user_4', '5d398480779fb318087520d6'),
('user_5', '5b2cae5cb2682a976914c2a1'),
('user_6', '5b2cae5cb2682a976914c2a2'),
('user_7', '5b2cae5cb2682a976914c2a3'),
('user_5', '5b2cae5cb2682a976914c2a4'),
('user_6', '5b2cae5cb2682a976914c2a5'),
('user_9', '5b2cae5cb2682a976914c2a6'),
('user_9', '5b2cae5cb2682a976914c2a7'),
('user_9', '5b2cae5cb2682a976914c2a8'),
('user_10', '5d398480779fb31808752013'),
('user_15', '5d398480779fb31808752014'),
('user_19', '5d398480779fb31808752015');
