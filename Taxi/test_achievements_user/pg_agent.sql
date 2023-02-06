INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at
)
VALUES
    (1120000000252888, NOW(), 'webalex', 'webalex', 'webalex', '2000-01-01');


INSERT INTO agent.achievements
(key,created,name_tanker_key,description_tanker_key,img_active,img_inactive,hidden)
VALUES
('key_1','2021-01-01 00:00:00','achievement.key_1.name','achievement.key_1.description','img_active','img_inactive',FALSE),
('key_2','2021-01-01 00:00:01','achievement.key_2.name','achievement.key_2.description','img_active','img_inactive',FALSE),
('key_3','2021-01-01 00:00:02','achievement.key_3.name','achievement.key_3.description','img_active','img_inactive',FALSE),
('key_4','2021-01-01 00:00:00','achievement.key_4.name','achievement.key_4.description','img_active','img_inactive',FALSE),
('key_5','2021-01-01 00:00:01','achievement.key_5.name','achievement.key_5.description','img_active','img_inactive',FALSE),
('key_6','2021-01-01 00:00:02','achievement.key_6.name','achievement.key_6.description','img_active','img_inactive',FALSE),
('key_7','2021-01-01 00:00:02','achievement.key_7.name','achievement.key_7.description','img_active','img_inactive',FALSE),
('key_8','2021-01-01 00:00:02','achievement.key_8.name','achievement.key_8.description','img_active','img_inactive',FALSE),
('key_9','2021-01-01 00:00:02','achievement.key_9.name','achievement.key_9.description','img_active','img_inactive',FALSE);




INSERT INTO agent.achievements_collections VALUES ('2c04b547a3da476e85b50ead69db1970','Первая коллекция');

INSERT INTO agent.achievements_collections_settings VALUES
(
 '2c04b547a3da476e85b50ead69db1970',
 'key_1',
 1
),
(
 '2c04b547a3da476e85b50ead69db1970',
 'key_2',
 2
),
(
 '2c04b547a3da476e85b50ead69db1970',
 'key_3',
 3
),
(
 '2c04b547a3da476e85b50ead69db1970',
 'key_4',
 4
),
(
 '2c04b547a3da476e85b50ead69db1970',
 'key_5',
 5
),
(
 '2c04b547a3da476e85b50ead69db1970',
 'key_6',
 6
),
(
 '2c04b547a3da476e85b50ead69db1970',
 'key_7',
 7
),
(
 '2c04b547a3da476e85b50ead69db1970',
 'key_8',
 8
),
(
 '2c04b547a3da476e85b50ead69db1970',
 'key_9',
 9
);

INSERT INTO agent.users_achievements VALUES
('2021-01-01 00:00:00+0000','key_1','webalex'),
('2021-01-02 00:00:00+0000','key_2','webalex'),
('2021-01-03 00:00:00+0000','key_3','webalex'),
('2021-01-04 00:00:00+0000','key_4','webalex'),
('2021-01-05 00:00:00+0000','key_5','webalex'),
('2021-01-06 00:00:00+0000','key_6','webalex');



INSERT INTO agent.permissions VALUES
    ('user_calltaxi', NOW(), NOW(), 'webalex', 'user_calltaxi', 'user_calltaxi', 'user_calltaxi', 'user_calltaxi');

INSERT INTO agent.roles VALUES
    ('calltaxi', NOW(), NOW(), 'webalex', 'calltaxi', 'calltaxi', 'calltaxi', 'calltaxi');

INSERT INTO agent.roles_permissions VALUES
    ('calltaxi', 'user_calltaxi', '2021-01-01 00:00:00', 'webalex');
INSERT INTO agent.users_roles VALUES
    (1, '2021-01-01 00:00:00', 'webalex', 'calltaxi');
