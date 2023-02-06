INSERT INTO agent.db_last_sync
VALUES ('key_2','2021-01-01 00:00:00'::timestamp);


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
 'permission_1',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'permission_1',
 'permission_1',
 'permission_1',
 'permission_1'

),
(
 'permission_2',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'permission_2',
 'permission_2',
 'permission_2',
 'permission_2'

);

INSERT INTO agent.roles VALUES
(
 'yandex_taxi_team',
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
 'yandex_taxi_team',
 'permission_1',
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
'yandex_taxi_team'
);

INSERT INTO agent.teams
(key,name,en_name,permission,piece)
VALUES
('test1','Тестовая команда 1','Test team 1','permission_1',true),
('test2','Тестовая команда 2','Test team 2','permission_2',true);




INSERT INTO agent.goods (id,ru_name,en_name,type,created,creator,permission,ru_description,en_description,image_mds_id)
VALUES (1,'key_1','key_1','type_1',NOW(),'webalex','permission_1','key_1','key_1','static');

INSERT INTO agent.goods_detail (id,goods_id,created,creator,price,ru_attribute,en_attribute,amount)
VALUES (1,1,NOW(),'webalex',100,'key','key',100);
