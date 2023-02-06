INSERT INTO public.auth_user (id,username) VALUES (1,'slon'),(2,'korol'),(3,'meetka');
INSERT INTO public.compendium_calculations_ticket (date,user_id,sum_bo) VALUES ('2021-12-01',1,100),('2021-12-01',2,1000),('2021-12-01',3,5000);




INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at
)
VALUES
    (1120000000252888, NOW(), 'mikh-vasily', 'Василий', 'Михайлов', '2016-06-02'),
    (1120000000252889, NOW(), 'webalex', 'Александр', 'Иванов', '2016-06-02'),
    (1120000000252889, NOW(), 'akozhevina', 'Анна', 'Кожевина', '2016-06-02'),
    (1120000000252888, NOW(), 'slon', 'Василий', 'Слонов', '2016-06-02'),
    (1120000000252889, NOW(), 'korol', 'Александр', 'Король', '2016-06-02'),
    (1120000000252889, NOW(), 'meetka', 'Дмитрий', 'Борисов', '2016-06-02');


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
),
(
 'user_taxisupport',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'user_taxisupport',
 'user_taxisupport',
 'user_taxisupport',
 'user_taxisupport'
);

INSERT INTO agent.roles VALUES
(
 'yandex_calltaxi',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'yandex_call_taxi',
 'yandex_call_taxi',
 'yandex_call_taxi',
 'yandex_call_taxi',
 true
),
(
 'yandex_ms',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'yandex_call_taxi',
 'yandex_call_taxi',
 'yandex_call_taxi',
 'yandex_call_taxi',
 true
),
(
 'yandex_ms_and_calltaxi',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'yandex_call_taxi',
 'yandex_call_taxi',
 'yandex_call_taxi',
 'yandex_call_taxi',
 true
),
(
 'yandex_taxi_support',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'yandex_taxi_support',
 'yandex_taxi_support',
 'yandex_taxi_support',
 'yandex_taxi_support',
 true
);

INSERT INTO agent.roles_permissions VALUES
(
 'yandex_calltaxi',
 'user_calltaxi',
 '2021-01-01 00:00:00',
 'webalex'

),
(
 'yandex_ms',
 'user_ms',
 '2021-01-01 00:00:00',
 'webalex'

),(
 'yandex_ms_and_calltaxi',
 'user_calltaxi',
 '2021-01-01 00:00:00',
 'webalex'

),(
 'yandex_ms_and_calltaxi',
 'user_ms',
 '2021-01-01 00:00:00',
 'webalex'

),
('yandex_taxi_support',
 'user_taxisupport',
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
'yandex_calltaxi'
),
(
 '2020-01-01 00:00:00',
 'webalex',
 'yandex_ms'
),
(
 '2020-01-01 00:00:00',
 'akozhevina',
 'yandex_ms_and_calltaxi'
),
(
 '2020-01-01 00:00:00',
 'slon',
 'yandex_taxi_support'
),
(
 '2020-01-01 00:00:00',
 'korol',
 'yandex_taxi_support'
),
(
 '2020-01-01 00:00:00',
 'meetka',
 'yandex_taxi_support'
);


INSERT INTO agent.battle_pass_events VALUES
(1,'2021-01-01 00:00:00','2031-01-01 00:00:00','calltaxi'),
(2,'2021-01-01 00:00:00','2031-01-01 00:00:00','ms'),
(3,'2021-01-01 00:00:00','2031-01-01 00:00:00','taxisupport');


INSERT INTO agent.battle_pass_rating
(
 event,
 login,
 join_at,
 current_score,
 last_score,
 bo,
 attempts,
 is_join
)
VALUES
(
 1,
 'mikh-vasily',
 NOW(),
 100,
 0,
 1500,
 5,
 true
),
(
 3,
 'slon',
 NOW(),
 0,
 0,
 0,
 0,
 true
),
(
 3,
 'korol',
 NOW(),
 0,
 0,
 0,
 0,
 true
),
(
 3,
 'meetka',
 NOW(),
 0,
 0,
 0,
 0,
 true
);


INSERT INTO agent.teams VALUES
('team_1','team_1','user_calltaxi');

UPDATE agent.users SET team='team_1' WHERE login IN ('mikh-vasily');


