INSERT INTO agent.departments VALUES
('yandex',NOW(),NOW(),'Яндекс',null);




INSERT INTO agent.users (
    uid,
    created,
    login,
    first_name,
    last_name,
    en_first_name,
    en_last_name,
    join_at,
    department,
    telegram
)
VALUES (
    1120000000252888,
     NOW(),
    'webalex',
    'Александр',
    'Иванов',
    'Alexandr',
    'Ivanov',
    '2016-06-02',
    'yandex',
    '{"1e55e7049fc543dc9ebbb63c8fc4d7ed"}'
),
(
    1120000000252888,
     NOW(),
    'liambaev',
    'Лиам',
    'Баев',
    'Liam',
    'Baev',
    '2016-06-02',
    null,
    '{"1e55e7049fc543dc9ebbb63c8fc4d7ed"}'
),
(
    1120000000252888,
     NOW(),
    'orangevl',
    'Семен',
    'Решетняк',
    'Simon',
    'Reshetnyak',
    '2016-06-02',
    'yandex',
    '{"1e55e7049fc543dc9ebbb63c8fc4d7ed"}'
);

INSERT INTO agent.departments_heads VALUES
('orangevl','yandex','chief');


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
 'calltaxi',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'Calltaxi',
 'Calltaxi',
 'Calltaxi',
 'Calltaxi',
 true
);

INSERT INTO agent.roles_permissions VALUES
(
 'calltaxi',
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
'calltaxi'
),
(
'2020-01-01 00:00:00',
'liambaev',
'calltaxi'
);

INSERT INTO agent.teams VALUES
('calltaxi','Команда Calltaxi','user_calltaxi',false,'Team Calltaxi');
UPDATE agent.users SET team='calltaxi';

