INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at
)
VALUES
    (1120000000252888, NOW(), 'mikh-vasily', 'Тест', 'Тестовый', '2016-06-02'),
    (1120000000252889, NOW(), 'webalex', 'Тест1', 'Тестовый1', '2016-06-02'),
    (1120000000252890, NOW(), 'test3', 'Тест3', 'Тестовый3', '2016-06-02');

INSERT INTO agent.permissions VALUES
    ('read_admin_shop', NOW(), NOW(), 'mikh-vasily', 'test3', 'test3', 'test3', 'test3'),
    ('read_shop_test_taxi', NOW(), NOW(), 'mikh-vasily', 'test', 'test', 'test', 'test'),
    ('read_shop_test_eda', NOW(), NOW(),'mikh-vasily', 'test2', 'test2', 'test2', 'test2'),
    ('read_shop_test_lavka', NOW(), NOW(), 'mikh-vasily', 'test3', 'test3', 'test3', 'test3');

INSERT INTO agent.roles VALUES
    ('test_role', NOW(), NOW(), 'mikh-vasily', 'тест', 'test', 'тест', 'test');

INSERT INTO agent.roles_permissions VALUES
    ('test_role', 'read_admin_shop', '2021-01-01 00:00:00', 'mikh-vasily');

INSERT INTO agent.users_roles VALUES
    (1, '2021-01-01 00:00:00', 'mikh-vasily', 'test_role');


INSERT INTO agent.goods (
    id,ru_name,en_name, type, created, updated, creator, permission,ru_description,en_description, image_mds_id, visible
)
VALUES (
    1,
    'test_name',
    'test_name',
    'test_type',
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    'mikh-vasily',
    'read_shop_test_taxi',
    'test_description',
    'test_description',
    'test_image',
    true
), (
    2,
    '2test_name',
    '2test_name',
    '2test_type',
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    'mikh-vasily',
    'read_shop_test_eda',
    '2test_description',
    '2test_description',
    '2test_image',
    true
), (
    3,
    '3test_name',
    '3test_name',
    '3test_type',
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    'mikh-vasily',
    'read_shop_test_eda',
    '3test_description',
    '3test_description',
    '3test_image',
    false
), (
    4,
    '4test_name',
    '4test_name',
    '4test_type',
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    'mikh-vasily',
    'read_shop_test_eda',
    '4test_description',
    '4test_description',
    '4test_image',
    true
);

INSERT INTO agent.goods_detail (
    id, goods_id, created, updated, creator, price,ru_attribute,en_attribute, amount, visible
)
VALUES (
    1,
    1,
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    'mikh-vasily',
    222.33,
    'test_attr',
    'test_attr',
    2,
    true
),
(
    2,
    1,
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    'mikh-vasily',
    333.22,
    'test_attr2',
    'test_attr2',
    3,
    false
),
(
    3,
    1,
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    'mikh-vasily',
    4444.55,
    'test_attr3',
    'test_attr3',
    5,
    true
),
(
    4,
    2,
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    'mikh-vasily',
    111.33,
    '2test_attr',
    '2test_attr',
    7,
    true
),
(
    5,
    2,
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    'mikh-vasily',
    311.22,
    '2test_attr2',
    '2test_attr2',
    4,
    true
),
(
    6,
    2,
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    'mikh-vasily',
    4111.55,
    '2test_attr3',
    '2test_attr3',
    1,
    true
),
(
    7,
    3,
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    'mikh-vasily',
    111.33,
    '3test_attr',
    '3test_attr',
    7,
    false
),
(
    8,
    3,
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    'mikh-vasily',
    311.22,
    '3test_attr2',
    '3test_attr2',
    4,
    false
),
(
    9,
    3,
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    'mikh-vasily',
    4111.55,
    '3test_attr3',
    '3test_attr3',
    1,
    false
);


INSERT INTO agent.shop_categories (id, ru_name, en_name, image_link, position) VALUES
('test1','Test','Test','image',0),
('test2','Test','Test','image',1),
('test3','Test','Test','image',2);

INSERT INTO agent.shop_categories_goods (category_id, goods_id) VALUES ('test1',1),('test2',1),('test3',1),('test2',2),('test3',2);
