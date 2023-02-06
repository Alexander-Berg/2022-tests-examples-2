INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at
)
VALUES
    (1120000000252888, NOW(), 'login_1', 'login_1', 'login_1', '2000-01-01'),
    (1120000000252889, NOW(), 'login_2', 'login_2', 'login2', '2000-01-01'),
    (1120000000252889, NOW(), 'webalex', 'webalex', 'webalex', '2000-01-01');;



INSERT INTO agent.permissions VALUES
    ('write_achievements', NOW(), NOW(), 'login_1', 'write_achievements', 'write_achievements', 'write_achievements', 'tewrite_achievementsst');

INSERT INTO agent.roles VALUES
    ('admin', NOW(), NOW(), 'login_1', 'admin', 'admin', 'admin', 'admin');

INSERT INTO agent.roles_permissions VALUES
    ('admin', 'write_achievements', '2021-01-01 00:00:00', 'login_1');
INSERT INTO agent.users_roles VALUES
    (1, '2021-01-01 00:00:00', 'login_2', 'admin'),
    (2, '2021-01-01 00:00:00', 'webalex', 'admin');


INSERT INTO agent.achievements
(key,created,name_tanker_key,description_tanker_key,img_active,img_inactive,hidden)
VALUES
('key_3','2021-01-01 00:00:00','achievement.key_3.name','achievement.key_3.description','img_active','img_inactive',FALSE),
('key_4','2021-01-01 00:00:01','achievement.key_4.name','achievement.key_4.description','img_active','img_inactive',FALSE),
('key_5','2021-01-01 00:00:02','achievement.key_5.name','achievement.key_5.description','img_active','img_inactive',TRUE);


INSERT INTO agent.achievements_collections VALUES ('2c04b547a3da476e85b50ead69db1970','Первая коллекция'),('2c04b547a3da476e85b50ead88njff','Вторая коллекция'),('1791fd06c11b46d5a08f1fb32ded99b2','Третья пустая коллекция');

INSERT INTO agent.achievements_collections_settings (collection_id, achievement_id, coins, lootbox_skin) VALUES
(
 '2c04b547a3da476e85b50ead69db1970',
 'key_3',
 0,
 'rare_card'
),
(
 '2c04b547a3da476e85b50ead69db1970',
 'key_4',
 0,
 'common_card'
),
(
 '2c04b547a3da476e85b50ead69db1970',
 'key_5',
 0,
  'immortal_card'
),
(
 '2c04b547a3da476e85b50ead88njff',
 'key_3',
 0,
  'common_card'

),
(
 '2c04b547a3da476e85b50ead88njff',
 'key_4',
 0,
  'common_card'

),
(
 '2c04b547a3da476e85b50ead88njff',
 'key_5',
 0,
  'common_card'

);

