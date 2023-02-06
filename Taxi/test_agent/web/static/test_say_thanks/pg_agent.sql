INSERT INTO agent.users (login, uid, created, first_name, last_name, join_at) VALUES
('justmark0', 100500, NOW(), 'Mark', 'Nicholson', '2022-05-01'),
('user1', 100502, NOW(), 'user1', 'user1', '2022-05-01'),
('user2', 100503, NOW(), 'user2', 'user2', '2022-03-01'),
('user3', 100503, NOW(), 'user3', 'user3', '2022-06-01');

INSERT INTO agent.permissions (key,created,creator,ru_name,en_name,en_description,ru_description) VALUES
('user_thank',NOW(),'justmark0','user_thank','user_thank','user_thank','user_thank');


INSERT INTO agent.roles (key,created,creator,ru_name,en_name,ru_description,en_description,visible)
VALUES
('thank_role',NOW(),'justmark0','thank_role','thank_role','thank_role','thank_role',true);

INSERT INTO agent.roles_permissions (key_role,key_permission,created,creator) VALUES
('thank_role','user_thank',NOW(),'justmark0');

INSERT INTO agent.users_roles (created,login,key) VALUES
(NOW(),'justmark0','thank_role'),
(NOW(),'user1','thank_role'),
(NOW(),'user2','thank_role'),
(NOW(),'user3','thank_role');

INSERT INTO agent.achievements
(key,created,name_tanker_key,description_tanker_key,img_active,img_inactive,hidden)
VALUES
('thank','2021-01-01 00:00:00','achievement.thank.name','achievement.thank.description','img_active','img_inactive',FALSE);

INSERT INTO agent.thank (uid, login, from_login, thank_themes) VALUES
(1, 'justmark0', 'user1', '{sociable}'),
(2, 'justmark0', 'user2', '{fast_response}');


