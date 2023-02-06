INSERT INTO agent.chatterbox_available_lines
VALUES
('login_1', '{line_1}'),
('login_2', '{}');

INSERT INTO agent.chatterbox_lines_info
VALUES
('line_1', 'line_1_tanker_key', 'online', 0),
('line_2', 'line_2_tanker_key', 'online', 0);

INSERT INTO agent.departments (name,updated,created,key,parent) VALUES
('department_1',NOW(),NOW(),'department_1',null ),
('department_2',NOW(),NOW(),'department_2',null );

INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at, department
)
VALUES
    (1120000000252888, NOW(), 'login_1', 'first_name', 'last_name', '2016-06-02', 'department_1'),
    (1120000000252889, NOW(), 'login_2', 'first_name', 'last_name', '2016-06-02', 'department_1'),
    (1120000000252890, NOW(), 'login_3', 'first_name', 'last_name', '2016-06-02', 'department_2');

INSERT INTO agent.permissions VALUES
(
 'user_calltaxi',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'login_1',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi'
);

INSERT INTO agent.roles VALUES
(
 'calltaxi',
 '2021-01-01 00:00:00',
 null,
 'login_1',
 'text',
 'text',
 'text',
 'text',
 true
);

INSERT INTO agent.roles_permissions VALUES
(
 'calltaxi',
 'user_calltaxi',
 '2021-01-01 00:00:00',
 'login_1'
);

INSERT INTO agent.users_roles
(
 created,
 login,
 key
 )
VALUES
('2020-01-01 00:00:00','login_1','calltaxi'),
('2020-01-01 00:00:00','login_2','calltaxi');
