INSERT INTO agent.users (login, uid, created, first_name, last_name, join_at, telegram) VALUES
('justmark0', 100500, NOW(), 'Mark', 'Nicholson', NOW(), '{@justmark0}'),
('owebalexlogin', 100502, NOW(), 'Александр1', 'Иванов1', NOW(), '{@login_test, @test_another}'),
('web', 100503, NOW(), 'Александр3', 'Иванов3', NOW(), '{@login_test, @test_another}'),
('webalex', 100504, NOW(), 'Александр', 'Иванов', NOW(), '{@test_login, @another_test}'),
('user1', 100505, NOW(), 'Первый', 'Пользователь', NOW(), '{@user1}'),
('user2', 100506, NOW(), 'Второй', 'Пользователь', NOW(), '{@user2}'),
('user4', 100506, NOW(), 'Четвертый', 'Пользователь', NOW(), '{@user4}'),
('user3', 100507, NOW(), 'Третий', 'Пользователь', NOW(), '{@user3}');


INSERT INTO agent.permissions (key,created,creator,ru_name,en_name,en_description,ru_description) VALUES
('user_project1',NOW(),'justmark0','user_project1','user_project1','user_project1','user_project1'),
('user_project2',NOW(),'justmark0','user_project2','user_project2','user_project2','user_project2');


INSERT INTO agent.roles (key,created,creator,ru_name,en_name,ru_description,en_description,visible)
VALUES
('project1_role',NOW(),'justmark0','project1_role','project1_role','project1_role','project1_role',true),
('project2_role',NOW(),'justmark0','project2_role','project2_role','project2_role','project2_role',true);


INSERT INTO agent.roles_permissions (key_role,key_permission,created,creator) VALUES
('project1_role','user_project1',NOW(),'justmark0'),
('project2_role','user_project2',NOW(),'justmark0');


INSERT INTO agent.users_roles (created,login,key) VALUES
(NOW(),'justmark0','project1_role'),
(NOW(),'owebalexlogin','project1_role'),
(NOW(),'web','project1_role'),
(NOW(),'webalex','project1_role'),
(NOW(),'user1','project1_role'),
(NOW(),'user2','project1_role'),
(NOW(),'user2','project2_role'),
(NOW(),'user4','project1_role'),
(NOW(),'user4','project2_role'),
(NOW(),'user3','project2_role');
