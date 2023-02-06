INSERT INTO agent.users (
    uid,
    created,
    login,
    first_name,
    last_name,
    join_at
)
VALUES
(
1120000000252888,
NOW(),
'webalex',
'Александр',
'Иванов',
'2016-06-02'),
(
 1120000000252888,
 NOW(),
'topalyan',
'Ольга',
'Топалян',
'2016-06-02'
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

),
(
 'user_ms_support',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'user_ms_support',
 'user_ms_support',
 'user_ms_support',
 'user_ms_support'

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
),
(
 'agent_ms',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'agent_ms',
 'agent_ms',
 'agent_ms',
 'agent_ms',
 true
);

INSERT INTO agent.roles_permissions VALUES
(
 'agent_call_taxi',
 'user_calltaxi',
 '2021-01-01 00:00:00',
 'webalex'

),
(
 'agent_ms',
 'user_ms_support',
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
),
(
 '2020-01-01 00:00:00',
 'topalyan',
 'agent_ms'
);


