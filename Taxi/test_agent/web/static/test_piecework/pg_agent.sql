INSERT INTO agent.users (
    uid,
    created,
    login,
    first_name,
    last_name,
    join_at,
    piece,
    country,
    piecework_half_time)
VALUES (
    1120000000252888,
     NOW(),
    'webalex',
    'Александр',
    'Иванов',
    '2016-06-02',
    true,
    'ru',
    true
),
(
    1120000000252888,
     NOW(),
    'topalyan',
    'Ольга',
    'Иванова',
    '2016-06-02',
    true,
    null,
    false
),
(
    1120000000252888,
     NOW(),
    'a-topalyan',
    'Алина',
    'Топалян',
    '2016-06-02',
    true,
    'by',
    false
),
(
    1120000000252888,
     NOW(),
    'liambaev',
    'Лиам',
    'Баев',
    '2016-06-02',
    true,
    'ru',
    false
),
(
    1120000000252888,
     NOW(),
    'webalexbot',
    'Александр',
    'Иванов',
    '2016-06-02',
    true,
    'ru',
    false
),
(
    1120000000252888,
     NOW(),
    'agent',
    'agent',
    'agent',
    '2016-06-02',
    true,
    null,
    false
),
(
    1120000000252888,
     NOW(),
    'agent_2',
    'agent_2',
    'agent_2',
    '2016-06-02',
    true,
    'ru',
    false
),
(
    1120000000252888,
     NOW(),
    'agent_hrms',
    'agent_hrms',
    'agent_hrms',
    '2016-06-02',
    false,
    null,
    false
);


INSERT INTO agent.permissions VALUES
(
 'read_team_calltaxi',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Команда CallTaxi',
 'CallTaxi Team',
 'Команда CallTaxi',
 'CallTaxi Team'

),
(
 'read_users_calltaxi',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Команда CallTaxi',
 'CallTaxi Team',
 'Команда CallTaxi',
 'CallTaxi Team'

),
(
 'user_calltaxi',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Сотрудник CallTaxi',
 'CallTaxi Team',
 'Сотрудник CallTaxi',
 'CallTaxi Team'

),
(
 'user_hrms',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Сотрудник hrms',
 'Сотрудник hrms',
 'Сотрудник hrms',
 'Сотрудник hrms'
);

INSERT INTO agent.roles VALUES
(
 'support_call_taxi',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'Агент CallTaxi',
 'Agent CallTaxi',
 'Агент CallTaxi',
 'Agent CallTaxi',
 true
),
(
 'hrms',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'Агент hrms',
 'Agent hrms',
 'Агент hrms',
 'Agent hrms',
 true
);

INSERT INTO agent.roles_permissions VALUES
(
 'support_call_taxi',
 'read_team_calltaxi',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'support_call_taxi',
 'user_calltaxi',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'support_call_taxi',
 'read_users_calltaxi',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'hrms',
 'user_hrms',
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
 'support_call_taxi'
),
(
 '2020-01-01 00:00:00',
 'liambaev',
 'support_call_taxi'
),
(
 '2020-01-01 00:00:00',
 'a-topalyan',
 'support_call_taxi'
),
(
 '2020-01-01 00:00:00',
 'webalexbot',
 'support_call_taxi'
),
(
 '2020-01-01 00:00:00',
 'agent_2',
 'support_call_taxi'
),
(
 '2020-01-01 00:00:00',
 'agent_hrms',
 'hrms'
);



INSERT INTO agent.teams VALUES
('first_line_calltaxi','Команда 1','read_team_calltaxi',false,'first_line_calltaxi_en'),
('second_line_calltaxi','Команда 2','read_team_calltaxi',false,'second_line_calltaxi_en');


UPDATE agent.users SET team='first_line_calltaxi' WHERE login IN ('webalex','liambaev','agent_2');

INSERT INTO agent.user_history_team VALUES
('2021-01-01','webalex','first_line_calltaxi'),
('2021-01-16','webalex','second_line_calltaxi'),
('2021-01-01','liambaev','first_line_calltaxi'),
('2021-01-01','agent_2',null);

INSERT INTO public.auth_user (id,username) VALUES (1,'a-topalyan'),(2,'webalexbot');
INSERT INTO public.compendium_reserves (user_id, "limit", now_bo) VALUES (1,1777,0),(2,4321,0);






