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
'taxisupport_user',
'taxisupport_user',
'taxisupport_user',
'2016-06-02'),
(
 1120000000252888,
 NOW(),
'calltaxi_user',
'calltaxi_user',
'calltaxi_user',
'2016-06-02'
);

INSERT INTO agent.permissions VALUES
(
 'user_calltaxi',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'taxisupport_user',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi'
),
(
 'user_taxisupport',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'calltaxi_user',
 'user_taxisupport',
 'user_taxisupport',
 'user_taxisupport',
 'user_taxisupport'
);


INSERT INTO agent.roles VALUES
(
 'agent_calltaxi',
 '2021-01-01 00:00:00',
 null,
 'calltaxi_user',
 'agent_call_taxi',
 'agent_call_taxi',
 'agent_call_taxi',
 'agent_call_taxi',
 true
),
(
 'agent_taxisupport',
 '2021-01-01 00:00:00',
 null,
 'taxisupport_user',
 'agent_taxisupport',
 'agent_taxisupport',
 'agent_taxisupport',
 'agent_taxisupport',
 true
);


INSERT INTO agent.roles_permissions VALUES
(
 'agent_calltaxi',
 'user_calltaxi',
 '2021-01-01 00:00:00',
 'calltaxi_user'
),
(
 'agent_taxisupport',
 'user_taxisupport',
 '2021-01-01 00:00:00',
 'taxisupport_user'
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
'calltaxi_user',
'agent_calltaxi'
),
(
 '2020-01-01 00:00:00',
 'taxisupport_user',
 'agent_taxisupport'
);
