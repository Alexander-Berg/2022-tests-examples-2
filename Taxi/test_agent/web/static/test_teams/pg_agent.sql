INSERT INTO agent.users (login, uid, created, first_name, last_name, join_at) VALUES
('user', 100502, NOW(), 'user1', 'user1', NOW()),
('user_admin', 100503, NOW(), 'user2', 'user2', NOW());

INSERT INTO agent.permissions (key,created,creator,ru_name,en_name,en_description,ru_description) VALUES
('write_teams',NOW(),'user_admin','write_teams','write_teams','write_teams','write_teams'),
('test',NOW(),'user_admin','test','test','test','test'),
('user_test',NOW(),'user_admin','user_test','user_test','user_test','user_test'),
('user_testa',NOW(),'user_admin','user_testa','user_testa','user_testa','user_testa');

INSERT INTO agent.roles (key,created,creator,ru_name,en_name,ru_description,en_description,visible)
VALUES
('write_teams_role',NOW(),'user_admin','write_teams_role','write_teams_role','write_teams_role','write_teams_role',true);

INSERT INTO agent.roles_permissions (key_role,key_permission,created,creator) VALUES
('write_teams_role','write_teams',NOW(),'user_admin');

INSERT INTO agent.users_roles (created,login,key) VALUES
(NOW(),'user_admin','write_teams_role');

INSERT INTO agent.teams (key, name, permission, piece, en_name, use_reserves) VALUES
('key_2','key_2','user_test', False, 'key_2', False),
('key_3','name_ru','user_test', False, 'name_en', True);
