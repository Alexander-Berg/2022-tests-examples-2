INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at
)
VALUES
    (1120000000252888, NOW(), 'mikh-vasily', 'Василий', 'Михайлов', '2022-05-01'),
    (1120000000252889, NOW(), 'webalex', 'Александр', 'Иванов', '2022-04-30'),
    (1120000000252889, NOW(), 'akozhevina', 'Анна', 'Кожевина', '2021-06-01'),
    (1120000000252888, NOW(), 'slon', 'Василий', 'Слонов', '2022-06-01'),
    (1120000000252889, NOW(), 'korol', 'Александр', 'Король', '2021-06-01'),
    (1120000000252889, NOW(), 'meetka', 'Дмитрий', 'Борисов', '2021-05-30');

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
 'yandex_calltaxi'
),
(
 '2020-01-01 00:00:00',
 'akozhevina',
 'yandex_calltaxi'
),
(
 '2020-01-01 00:00:00',
 'slon',
 'yandex_ms'
),
(
 '2020-01-01 00:00:00',
 'korol',
 'yandex_ms'
),
(
 '2020-01-01 00:00:00',
 'meetka',
 'yandex_ms'
);


INSERT INTO agent.achievements (key, created, name_tanker_key, description_tanker_key, img_active, img_inactive, hidden, updated) VALUES
('experience_1month',NOW(),'achievement.experience_1month.name','achievement.experience_1month.description','https://jing.yandex-team.ru/files/liambaev/1month.svg','https://jing.yandex-team.ru/files/liambaev/1month_disabled.svg',false,NOW()),
('experience_1year',NOW(),'achievement.experience_1year.name','achievement.experience_1year.description','https://jing.yandex-team.ru/files/liambaev/1year.svg','https://jing.yandex-team.ru/files/liambaev/1year_disabled.svg',false,NOW());

INSERT INTO agent.achievements_collections VALUES ('collection_1', 'collection_1_name'),('collection_2','collection_2_name');

INSERT INTO agent.achievements_collections_settings (collection_id, achievement_id, coins, lootbox_skin) VALUES ('collection_1','experience_1month',10,'common_card'),('collection_1','experience_1year',20,'rare_card'),('collection_2','experience_1month',0,'legendary_card'),('collection_2','experience_1year',50,'immortal_card');
