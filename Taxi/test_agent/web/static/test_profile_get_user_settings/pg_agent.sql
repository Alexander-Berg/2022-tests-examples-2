INSERT INTO agent.departments VALUES
('calltaxi',NOW(),NOW(),'Яндекс',null),
('market',NOW(),NOW(),'Яндекс',null);


INSERT INTO agent.users (
    uid,
    created,
    login,
    first_name,
    last_name,
    join_at,
    department
)
VALUES
(1120000000252888,NOW(),'chief', 'first_name', 'last_name', '2020-01-01', 'calltaxi'),
(1120000000252882,NOW(),'regular_login', 'first_name', 'last_name', '2020-01-01', 'calltaxi'),
(1120000000252882,NOW(),'empty_login', 'first_name', 'last_name', '2020-01-01', 'calltaxi'),
(1120000000252882,NOW(),'admin', 'first_name', 'last_name', '2020-01-01', NULL),
(1120000000252882,NOW(),'market_chief', 'first_name', 'last_name', '2020-01-01', 'market'),
(1120000000252882,NOW(),'market_login', 'first_name', 'last_name', '2020-01-01', 'market');


INSERT INTO agent.departments_heads VALUES
('chief','calltaxi','chief'),
('market_chief','market','chief');


INSERT INTO agent.permissions (key,created,creator,ru_name,en_name,en_description,ru_description) VALUES
('read_users_calltaxi',NOW(),'admin','read_users_calltaxi','read_users_calltaxi','read_users_calltaxi','read_users_calltaxi'),
('user_calltaxi',NOW(),'admin','user_calltaxi','user_calltaxi','user_calltaxi','user_calltaxi');


INSERT INTO agent.roles VALUES
(
 'role_with_view_settings_perm',
 '2021-01-01 00:00:00',
 null,
 'admin',
 'РОЛЬ',
 'ROLE',
 'РОЛЬ',
 'ROLE',
 true
),
(
 'role_user_calltaxi',
 '2021-01-01 00:00:00',
 null,
 'admin',
 'РОЛЬ',
 'ROLE',
 'РОЛЬ',
 'ROLE',
 true
);


INSERT INTO agent.roles_permissions VALUES
(
 'role_with_view_settings_perm',
 'read_users_calltaxi',
 '2021-01-01 00:00:00',
 'admin'
),
(
 'role_user_calltaxi',
 'user_calltaxi',
 '2021-01-01 00:00:00',
 'admin'
);


INSERT INTO agent.users_roles
(
 created,
 login,
 key
 )
VALUES
(
'2020-01-01 00:00:00',
'admin',
'role_with_view_settings_perm'
),
(
'2020-01-01 00:00:00',
'regular_login',
'role_user_calltaxi'
),
(
'2020-01-01 00:00:00',
'empty_login',
'role_user_calltaxi'
);


INSERT INTO agent.teams
(key,name,en_name,permission,piece)
VALUES
('team_1','КОМАНДА 1','TEAM 1','user_calltaxi',true);

UPDATE agent.users SET team='team_1';


INSERT INTO agent.chatterbox_support_settings
(
    login,
    assigned_lines,
    can_choose_from_assigned_lines,
    can_choose_except_assigned_lines,
    max_chats,
    languages,
    work_off_shift
)
VALUES
('regular_login', '{line_1,line_2}', TRUE, TRUE, 12, '{ru,en}', TRUE);


INSERT INTO agent.chatterbox_available_lines
(
    login,
    lines
)
VALUES
('regular_login', '{line_1, line_2, line_3}');


INSERT INTO agent.chatterbox_lines_info
(
    line,
    line_tanker_key,
    mode
)
VALUES
('line_1','line_1_tanker_key','online'),
('line_2','line_2_tanker_key','online'),
('line_3','line_3_tanker_key','offline');
