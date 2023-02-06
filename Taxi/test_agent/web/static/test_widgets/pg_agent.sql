INSERT INTO agent.users (
    uid,
    created,
    login,
    first_name,
    last_name,
    join_at
)
VALUES (
    1120000000252888,
     NOW(),
    'webalex',
    'Александр',
    'Иванов',
    '2016-06-02'
);



INSERT INTO agent.permissions VALUES
(
 'widget_quality',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Виджет качества',
 'Widget quality',
 'Виджет качества',
 'Widget quality'

),
(
 'widget_csat',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Виджет CSAT',
 'Widget CSAT',
 'Виджет CSAT',
 'Widget CSAT'

),
(
 'widget_tph',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Виджет TPH',
 'Widget TPH',
 'Виджет TPH',
 'Widget TPH'

);



INSERT INTO agent.roles VALUES
(
 'yandex_taxi_agent',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'Агент поддержки яндекс такси',
 'support taxi',
 'Агент поддержки яндекс такси',
 'Support Yandex taxi',
 true

);


INSERT INTO agent.roles_permissions VALUES
(
 'yandex_taxi_agent',
 'widget_quality',
 '2021-01-01 00:00:00',
 'webalex'

),
(

 'yandex_taxi_agent',
 'widget_csat',
 '2021-01-01 00:00:00',
 'webalex'

),
(
 'yandex_taxi_agent',
 'widget_tph',
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
 'yandex_taxi_agent'
)

