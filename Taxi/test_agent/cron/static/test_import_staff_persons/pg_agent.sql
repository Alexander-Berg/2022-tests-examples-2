INSERT INTO agent.departments VALUES ('yandex',NOW(),NOW(),'Яндекс',null), ('something_dep',NOW(),NOW(),'Департмент',null);

INSERT INTO agent.users (login, uid, created, first_name, last_name, join_at) VALUES
('liambaev', 100500, NOW(), 'Лиам', 'Баев', NOW()),
('webalex', 100500, NOW(), 'Лиам', 'Баев', NOW()),
('orangevl', 100500, NOW(), 'Лиам', 'Баев', NOW()),
('dismissed_user', 100500, NOW(), 'dismissed_user', 'dismissed_user', NOW());

INSERT INTO agent.permissions (key, created, creator, ru_name, en_name) VALUES ('user_calltaxi', NOW(), 'liambaev', 'юзер калл тахи', 'user call taxi');

INSERT INTO agent.teams VALUES ('standart', 'Стандарт', 'user_calltaxi');

INSERT INTO agent.roles (key, created, creator, visible, ru_name, en_name) VALUES ('calltaxi_support', NOW(), 'liambaev', 't', 'калл тахи суппорт', 'call taxi sup');

INSERT INTO agent.roles_permissions VALUES ('calltaxi_support', 'user_calltaxi', NOW(), 'liambaev');

INSERT INTO agent.users_roles VALUES (1, NOW(), 'webalex', 'calltaxi_support'),(2, NOW(), 'liambaev', 'calltaxi_support'),(3, NOW(), 'orangevl', 'calltaxi_support');

UPDATE agent.users SET team='standart' WHERE login='dismissed_user'
