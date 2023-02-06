INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at,team
)
VALUES
    (1120000000252888, NOW(), 'liambaev', 'Лиам', 'Баев', '2016-06-02',null ),
    (1120000000252889, NOW(), 'webalex', 'Александр', 'Иванов', '2016-06-02',null),
    (1120000000252889, NOW(), 'login_1', 'login_1', 'login_1', '2016-06-02',null),
    (1120000000252889, NOW(), 'login_2', 'login_2', 'login_2', '2016-06-02',null),
    (1120000000252889, NOW(), 'login_3', 'login_3', 'login_3', '2016-06-02',null),
    (1120000000252889, NOW(), 'login_4', 'login_4', 'login_4', '2016-06-02',null);

INSERT INTO agent.permissions VALUES
    ('user', NOW(), NOW(), 'webalex', 'user', 'user', 'user', 'user');

INSERT INTO agent.teams (key,name,permission,piece,en_name,use_reserves)
VALUES
    ('team_1','Team 1','user',false,'Team 1',false),
    ('team_2','Team 2','user',false,'Team 2',false),
    ('team_3','Team 3','user',false,'Team 3',false);


UPDATE agent.users SET team='team_1' WHERE login IN ('liambaev','webalex','login_1');


INSERT INTO agent.roles VALUES
(
 'support',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'support',
 'support',
 'support',
 'support',
 true
);

INSERT INTO agent.roles_permissions VALUES
(
 'support',
 'user',
 '2021-01-01 00:00:00',
 'webalex'
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
'webalex',
'support'
);


INSERT INTO agent.mass_notifications
(
 id,
 creator,
 created_at,
 target_users,
 viewed_users,
 title,
 body,
 link,
 type,
 targets
)
VALUES
(
 '63cae574fca043d8833d7bb9a9bb7ef1',
 'webalex',
 '2022-04-20 15:03:02',
 100,
 0,
 'Title 1',
 'Body 1',
 'url 1',
 'warning',
 '[{"type": "teams", "value": ["calls"]}]'
),
(
 'faadb32303664af38b75ff2653e1bb43',
 'webalex',
 '2022-04-20 16:10:02',
 100,
 0,
 'Title 2',
 'Body 2',
 'url 2',
 'warning',
 '[{"type": "projects", "value": ["calltaxi"]}]'
);
