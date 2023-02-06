INSERT INTO agent.users (login, uid, created, first_name, last_name, join_at) VALUES
('calltaxi_support', 123, NOW(), 'calltaxi_support', 'calltaxi_support', NOW()),
('calltaxi_support_wrong_status', 123, NOW(), 'calltaxi_support', 'calltaxi_support', NOW()),
('calltaxi_support_too_much_money', 123, NOW(), 'calltaxi_support', 'calltaxi_support', NOW()),
('directsupport_support', 123, NOW(), 'directsupport_support', 'directsupport_support', NOW());


INSERT INTO agent.users_payday
(
    login,
    payday_uuid,
    status
)
VALUES
('calltaxi_support','calltaxi_support', 'active'),
('calltaxi_support_wrong_status','calltaxi_support_wrong_status', 'dada'),
('calltaxi_support_too_much_money','calltaxi_support_too_much_money', 'active'),
('directsupport_support','directsupport_support', 'active');


INSERT INTO agent.permissions (key,created,creator,ru_name,en_name,en_description,ru_description) VALUES
('user_calltaxi',NOW(),'calltaxi_support','user_calltaxi','user_calltaxi','user_calltaxi','user_calltaxi'),
('user_directsupport',NOW(),'calltaxi_support','user_directsupport','user_directsupport','user_directsupport','user_directsupport');


INSERT INTO agent.roles VALUES
(
 'role_user_calltaxi',
 '2021-01-01 00:00:00',
 null,
 'calltaxi_support',
 'РОЛЬ',
 'ROLE',
 'РОЛЬ',
 'ROLE',
 true
),
(
 'role_user_directsupport',
 '2021-01-01 00:00:00',
 null,
 'directsupport_support',
 'РОЛЬ',
 'ROLE',
 'РОЛЬ',
 'ROLE',
 true
);


INSERT INTO agent.roles_permissions VALUES
(
 'role_user_calltaxi',
 'user_calltaxi',
 '2021-01-01 00:00:00',
 'calltaxi_support'
),
(
 'role_user_directsupport',
 'user_directsupport',
 '2021-01-01 00:00:00',
 'calltaxi_support'
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
'calltaxi_support',
'role_user_calltaxi'
),
(
'2020-01-01 00:00:00',
'calltaxi_support_wrong_status',
'role_user_calltaxi'
),
(
'2020-01-01 00:00:00',
'calltaxi_support_too_much_money',
'role_user_calltaxi'
),
(
'2020-01-01 00:00:00',
'directsupport_support',
'role_user_directsupport'
);
