INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at
)
VALUES
    (1120000000252888, NOW(), 'mikh-vasily', 'Василий', 'Михайлов', '2016-06-02'),
    (1120000000252889, NOW(), 'webalex', 'Александр', 'Иванов', '2016-06-02'),
    (1120000000252889, NOW(), 'akozhevina', 'Анна', 'Кожевина', '2016-06-02'),
    (1120000000252889, NOW(), 'liambaev', 'Лиам', 'Баев', '2016-06-02');


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
'liambaev',
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
);


INSERT INTO agent.battle_pass_events VALUES
(1,'2020-12-31 21:00:00','2030-12-31 21:00:00','calltaxi','snowflake'),
(2,'2020-12-31 21:00:00','2030-12-31 21:00:00','ms','snowflake');

INSERT INTO agent.battle_pass_rating (event,login,current_score,last_score,bo,attempts,is_join)
VALUES (1,'mikh-vasily',0,0,0,0,false),(1,'liambaev',100,0,0,0,true);


INSERT INTO agent.billing_operations_history
(id,doc_id,dt,login,project,value,operation_type,section_type,description,viewed)
VALUES
(1,1,NOW(),'mikh-vasily','calltaxi',100,'payment_deposit','bp','bp',false);
