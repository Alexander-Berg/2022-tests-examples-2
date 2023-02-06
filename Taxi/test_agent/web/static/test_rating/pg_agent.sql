INSERT INTO agent.users (
    uid,
    created,
    login,
    first_name,
    last_name,
    join_at,
    country
)
VALUES (
    1120000000252888,
     NOW(),
    'webalex',
    'Александр',
    'Иванов',
    '2016-06-02',
    'ru'
),
(
    1120000000252888,
     NOW(),
    'liambaev',
    'Лиам',
    'Баев',
    '2016-06-02',
    'ru'
),
(
    1120000000252888,
     NOW(),
    'piskarev',
    'Александр',
    'Пискарёв',
    '2016-06-02',
    'ru'
),
(
    1120000000252888,
     NOW(),
    'akozhevina',
    'Анна',
    'Кожевина',
    '2016-06-02',
    'by'
),
(
    1120000000252888,
     NOW(),
    'simon',
    'Семён',
    'Семёныч',
    '2016-06-02',
    'by'
);

INSERT INTO agent.permissions VALUES
(
 'user_calltaxi',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi'

);

INSERT INTO agent.roles VALUES
(
 'agent_call_taxi',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'agent_call_taxi',
 'agent_call_taxi',
 'agent_call_taxi',
 'agent_call_taxi',
 true
);

INSERT INTO agent.roles_permissions VALUES
(
 'agent_call_taxi',
 'user_calltaxi',
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
 'agent_call_taxi'
);

INSERT INTO agent.teams VALUES ('first_calltaxi','first_calltaxi','user_calltaxi');

UPDATE agent.users SET team='first_calltaxi';


