INSERT INTO agent.users (login, uid, created, first_name, last_name, join_at) VALUES
('justmark0', 100500, NOW(), 'Mark', 'Nicholson', NOW()),
('romford', 100500, NOW(), 'Alexander', 'Fedotov', NOW()),
('webalex', 100500, NOW(), 'Alexander', 'Ivanov', NOW()),
('admin', 100500, NOW(), 'admin', 'admin', NOW());

INSERT INTO agent.permissions (key,created,creator,ru_name,en_name,en_description,ru_description) VALUES
('news_view_all_teams_and_projects',NOW(),'webalex','news_view_all_teams_and_projects','news_view_all_teams_and_projects','news_view_all_teams_and_projects','news_view_all_teams_and_projects'),
('user_project_1_perm',NOW(),'webalex','user_project_1_perm','user_project_1_perm','user_project_1_perm','user_project_1_perm'),
('user_project_2_perm',NOW(),'webalex','user_project_2_perm','user_project_2_perm','user_project_2_perm','user_project_2_perm');

INSERT INTO agent.roles (key,created,creator,ru_name,en_name,ru_description,en_description,visible)
VALUES
('admin',NOW(),'webalex','admin','admin','admin','admin',true),
('project_1_role',NOW(),'webalex','project_1_role','project_1_role','project_1_role','project_1_role',true),
('project_2_role',NOW(),'webalex','project_2_role','project_2_role','project_2_role','project_2_role',true);


INSERT INTO agent.roles_permissions (key_role,key_permission,created,creator) VALUES
('project_1_role','user_project_1_perm',NOW(),'webalex'),
('project_2_role','user_project_2_perm',NOW(),'webalex'),
('admin','news_view_all_teams_and_projects',NOW(),'webalex');

INSERT INTO agent.users_roles
(
 created,
 login,
 key
 )
VALUES
('2020-01-01 00:00:00','justmark0','project_1_role'),
('2020-01-01 00:00:00','admin','admin'),
('2020-01-01 00:00:00','romford','project_1_role'),
('2020-01-01 00:00:00','romford','project_2_role');

INSERT INTO agent.teams
(key,name,en_name,permission,piece)
VALUES
('team_1','team_1','team_1_en','user_project_1_perm',true),
('team_2','team_2','team_2_en','user_project_1_perm',true),
('team_3','team_3','team_3_en','user_project_2_perm',true),
('team_4','team_4','team_4_en','user_project_2_perm',true);
