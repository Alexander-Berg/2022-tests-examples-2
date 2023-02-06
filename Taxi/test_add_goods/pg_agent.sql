INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at
)
VALUES
    (1120000000252888, NOW(), 'mikh-vasily', 'Тест', 'Тестовый', '2016-06-02'),
    (1120000000252889, NOW(), 'webalex', 'Тест1', 'Тестовый1', '2016-06-02');

INSERT INTO agent.permissions VALUES
    ('read_shop_test_taxi', NOW(), NOW(), 'mikh-vasily', 'test', 'test', 'test', 'test'),
    ('write_admin_shop', NOW(), NOW(), 'mikh-vasily', 'test', 'test', 'test', 'test');


INSERT INTO agent.roles VALUES
    ('test_role', NOW(), NOW(), 'mikh-vasily', 'тест', 'test', 'тест', 'test');

INSERT INTO agent.roles_permissions VALUES
    ('test_role', 'read_shop_test_taxi', '2021-01-01 00:00:00', 'mikh-vasily'),
    ('test_role', 'write_admin_shop', '2021-01-01 00:00:00', 'mikh-vasily');

INSERT INTO agent.users_roles VALUES
    (1, '2021-01-01 00:00:00', 'mikh-vasily', 'test_role');


INSERT INTO agent.shop_categories (id, ru_name, en_name, image_link, position) VALUES
('test1','Test','Test','image',0),
('test2','Test','Test','image',1),
('test3','Test','Test','image',2);
