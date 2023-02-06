INSERT INTO agent.users (login, uid, created, first_name, last_name, join_at) VALUES
('justmark0', 100500, NOW(), 'Mark', 'Nicholson', NOW()),
('user_without_permission', 100501, NOW(), 'user_without_permission', 'user_without_permission', NOW()),
('user1', 100502, NOW(), 'user1', 'user1', NOW()),
('user2', 100503, NOW(), 'user2', 'user2', NOW());

INSERT INTO agent.permissions (key,created,creator,ru_name,en_name,en_description,ru_description) VALUES
('create_lootbox',NOW(),'justmark0','create_lootbox','create_lootbox','create_lootbox','create_lootbox');


INSERT INTO agent.roles (key,created,creator,ru_name,en_name,ru_description,en_description,visible)
VALUES
('create_lootbox_role',NOW(),'justmark0','create_lootbox_role','create_lootbox_role','create_lootbox_role','create_lootbox_role',true);

INSERT INTO agent.roles_permissions (key_role,key_permission,created,creator) VALUES
('create_lootbox_role','create_lootbox',NOW(),'justmark0');

INSERT INTO agent.users_roles (created,login,key) VALUES
(NOW(),'justmark0','create_lootbox_role');

INSERT INTO agent.lootboxes (id, login, created_at, description, coins, image, skin, viewed) VALUES
('a111000222', 'justmark0', NOW(), 'happy birthday', NULL, NULL, 'gold confetti', false),
('1233', 'user2', NOW(), 'happy birthday0', NULL, 'link0', 'gold confetti', true),
('1234', 'user2', NOW(), 'happy birthday1', NULL, 'link1', 'gold confetti', false),
('1235', 'user2', NOW(), 'happy birthday2', 12, NULL, 'gold confetti',false),
('1236', 'user2', NOW(), 'happy birthday3', 0, NULL, 'pink confetti',false);

