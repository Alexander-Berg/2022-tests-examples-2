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
),
(
    1120000000252888,
     NOW(),
    'liam',
    'liam',
    'liam',
    '2016-06-02'
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
 'dismiss_users',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Возможность уволить сотруднкиа',
 'Can dismiss users',
 'Возможность уволить сотруднкиа',
 'Can dismiss users'

),
(
 'naim_users',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'Найм сотрудников',
 'Naim users',
 'Найм сотрудников',
 'Naim users'

),
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

),
(
 'support_calltaxi',
 '2021-01-01 00:00:00',
 null,
 'webalex',
 'Агент calltaxi',
 'support calltaxi',
 'Агент calltaxi',
 'Support calltaxi',
 false
);


INSERT INTO agent.roles_permissions VALUES
(
 'yandex_taxi_agent',
 'approve_piecework',
 '2021-01-01 00:00:00',
 'webalex'

),
(

 'yandex_taxi_agent',
 'naim_users',
 '2021-01-01 00:00:00',
 'webalex'

),
(
 'yandex_eda_agent',
 'dismiss_users',
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
 'support_calltaxi',
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
 'yandex_eda_agent'
),
(
 '2020-01-01 00:00:00',
 'webalex',
 'yandex_taxi_agent'
),
(
 '2020-01-01 00:00:00',
 'liam',
 'support_calltaxi'
);



