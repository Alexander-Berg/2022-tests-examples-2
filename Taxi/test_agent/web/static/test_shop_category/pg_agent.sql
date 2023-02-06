INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at
)
VALUES
    (1120000000252888, NOW(), 'admin', 'Тест', 'Тестовый', '2016-06-02'),
    (1120000000252889, NOW(), 'login', 'Тест1', 'Тестовый1', '2016-06-02');


INSERT INTO agent.permissions VALUES
    ('write_admin_shop', NOW(), NOW(), 'admin', 'test', 'test', 'test', 'test');

INSERT INTO agent.roles VALUES
    ('admin', NOW(), NOW(), 'admin', 'тест', 'test', 'тест', 'test');

INSERT INTO agent.roles_permissions VALUES
    ('admin', 'write_admin_shop', '2021-01-01 00:00:00', 'admin');

INSERT INTO agent.users_roles VALUES
    (1, '2021-01-01 00:00:00', 'admin', 'admin');


INSERT INTO agent.shop_categories (id,ru_name,en_name,image_link,position)
VALUES ('12345','Категория','Category','img_link',1);




