
INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at, birthday
)
VALUES
    (1120000000252889, NOW(), 'webalex', 'Александр', 'Иванов', '2016-06-02', '2000-03-01'),
    (1120000000252889, NOW(), 'justmark0', 'Марк', 'Николсон', '2016-06-02', '2000-02-29'),
    (1120000000252889, NOW(), 'unholy', 'Нияз', 'Наибулин', '2016-06-02', '2000-03-02'),
    (1120000000252888, NOW(), 'mikh-vasily', 'Василий', 'Михайлов', '2016-06-02', '2000-02-28'),
    (1120000000252889, NOW(), 'akozhevina', 'Анна', 'Кожевина', '2016-06-02', '2000-03-01');


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
 'user_ms',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'user_ms',
 'user_ms',
 'user_ms',
 'user_ms'
);

INSERT INTO agent.roles VALUES
(
 'user_calltaxi',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'user_call_taxi',
 'user_call_taxi',
 'user_call_taxi',
 'user_call_taxi',
 true
),
(
 'user_ms',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'user_call_taxi',
 'user_call_taxi',
 'user_call_taxi',
 'user_call_taxi',
 true
);

INSERT INTO agent.roles_permissions VALUES
(
 'user_calltaxi',
 'user_calltaxi',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'user_ms',
 'user_ms',
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
'mikh-vasily',
'user_calltaxi'
),
(
 '2020-01-01 00:00:00',
 'webalex',
 'user_calltaxi'
),
(
 '2020-01-01 00:00:00',
 'justmark0',
 'user_calltaxi'
),
(
 '2020-01-01 00:00:00',
 'unholy',
 'user_calltaxi'
),
(
 '2020-01-01 00:00:00',
 'akozhevina',
 'user_ms'
);

INSERT INTO agent.created_lootboxes (type, login, coins, description, skin, given_at) VALUES ('birthday', 'akozhevina', 7, 'С Днем Рождения!', 'rare_card', '2021-03-01 00:01:00.000000 +00:00');
