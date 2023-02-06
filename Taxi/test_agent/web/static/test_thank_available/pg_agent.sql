INSERT INTO agent.users (login, uid, created, first_name, last_name, join_at) VALUES
('justmark0', 100500, NOW(), 'Mark', 'Nicholson', '2022-06-01'),
('user1', 100502, NOW(), 'user1', 'user1', '2022-05-01'),
('user2', 100503, NOW(), 'user2', 'user2', '2022-03-01');

INSERT INTO agent.thank_suggestion (uid, login, created_at) VALUES
(1, 'user2', '2022-04-10');
