INSERT INTO agent.users (
    uid,
    created,
    login,
    first_name,
    last_name,
    join_at)
VALUES (
    1120000000252888,
     NOW(),
    'liambaev',
    'Лиам',
    'Баев',
    NOW()),
(
    1120000000252888,
     NOW(),
    'device',
    'Алексей',
    'Сухарь',
    NOW());


INSERT INTO agent.permissions VALUES
(
 'user_calltaxi',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'liambaev',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi'

),
(
 'read_users_calltaxi',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'liambaev',
 'read_users_calltaxi',
 'read_users_calltaxi',
 'read_users_calltaxi',
 'read_users_calltaxi'
);

INSERT INTO agent.roles VALUES
(
 'user_calltaxi',
 '2021-01-01 00:00:00',
 null,
 'liambaev',
 'User calltaxi',
 'User calltaxi',
 'User calltaxi',
 'User calltaxi',
 true
),
(
 'head_calltaxi',
 '2021-01-01 00:00:00',
 null,
 'liambaev',
 'Head calltaxi',
 'Head calltaxi',
 'Head calltaxi',
 'Head calltaxi',
 true
);

INSERT INTO agent.roles_permissions VALUES
(
 'user_calltaxi',
 'user_calltaxi',
 '2021-01-01 00:00:00',
 'liambaev'
),
(
 'head_calltaxi',
 'read_users_calltaxi',
 '2021-01-01 00:00:00',
 'liambaev'
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
'liambaev',
'user_calltaxi'
),
(
'2020-01-01 00:00:00',
'device',
'head_calltaxi'
);


INSERT INTO agent.gp_details_quality VALUES
(
 'TEST_1',
 'liambaev',
 '2022-01-31 21:00:00',
 '2022-01-31 21:00:00',
 '2022-01-31 21:00:00',
 'commutation_queue_code_value',
 'ticket_type_code_value',
 0,
 'dialog_url_value',
 'auditor_comment_value'
),
(
 'TEST_2',
 'liambaev',
 '2022-01-31 22:00:00',
 '2022-01-31 22:00:00',
 '2022-01-31 22:00:00',
 'commutation_queue_code',
 'ticket_type_code',
 0,
 'dialog_url',
 'auditor_comment'
),
(
 'TEST_3',
 'liambaev',
 '2022-01-31 23:00:00',
 '2022-01-31 23:00:00',
 '2022-01-31 23:00:00',
 'commutation_queue_code',
 'ticket_type_code',
 0,
 'dialog_url',
 'auditor_comment'
);
