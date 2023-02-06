INSERT INTO agent.users (
    uid,
    created,
    login,
    first_name,
    last_name,
    join_at,
    source
)
VALUES (
    1120000000252888,
     NOW(),
    'webalex',
    'Александр',
    'Иванов',
    '2016-06-02',
    'yateam_staff'
),
(
    1120000000252888,
     NOW(),
    'outstaff_login',
    'Александр',
    'Пирогов',
    '2016-06-02',
    'lavka-offline'
);



INSERT INTO agent.permissions VALUES
(
 'approve_piecework',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Окание сделки',
 'Ok piecework',
 'Окание сделки',
 'Ok piecework'

),
(
 'approve_piecework_logistic',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Окание сделки логистики',
 'Ok piecework logic',
 'Окание сделки логистики',
 'Ok piecework logic'

),
                                     (
 'test1',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Окание сделки логистики',
 'Ok piecework logic',
 'Окание сделки логистики',
 'Ok piecework logic'

),
                                     (
 'test2',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Окание сделки логистики',
 'Ok piecework logic',
 'Окание сделки логистики',
 'Ok piecework logic'

),
(
 'test3',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Окание сделки логистики',
 'Ok piecework logic',
 'Окание сделки логистики',
 'Ok piecework logic'

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

),
                               (
 'yandex_eda_agent',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'Агент поддержки яндекс еда',
 'support eda',
 'Агент поддержки яндекс еда',
 'Support Yandex eda',
 false

);


INSERT INTO agent.roles_permissions VALUES
(
 'yandex_eda_agent',
 'approve_piecework',
 '2021-01-01 00:00:00',
 'webalex'

),
(
 'yandex_eda_agent',
 'approve_piecework_logistic',
 '2021-01-01 00:00:00',
 'webalex'
),
(
 'yandex_taxi_agent',
 'approve_piecework_logistic',
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
),
(
 '2020-01-01 00:00:00',
 'outstaff_login',
 'yandex_taxi_agent'
);



