INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at
)
VALUES
    (1120000000252888, NOW(), 'mikh-vasily', 'Тест', 'Тестовый', '2016-06-02'),
    (1120000000252889, NOW(), 'webalex', 'Тест1', 'Тестовый1', '2016-06-02'),
    (1120000000252889, NOW(), 'test_user', 'Тест2', 'Тестовый2', '2016-06-02');

INSERT INTO agent.permissions VALUES
(
    'read_shop_test_taxi',
    NOW(),
    NOW(),
    'mikh-vasily',
    'test',
    'test',
    'test',
    'test'
),
(
    'read_shop_test_eda',
    NOW(),
    NOW(),
    'mikh-vasily',
    'test',
    'test',
    'test',
    'test'
),
(
    'read_shop_test_lavka',
    NOW(),
    NOW(),
    'mikh-vasily',
    'test',
    'test',
    'test',
    'test'
);

INSERT INTO agent.roles VALUES
    ('test_role', NOW(), NOW(), 'mikh-vasily', 'тест', 'test', 'тест', 'test'),
    ('test_role1', NOW(), NOW(), 'mikh-vasily', 'тест', 'test', 'тест', 'test');

INSERT INTO agent.roles_permissions VALUES
    ('test_role', 'read_shop_test_taxi', '2021-01-01 00:00:00', 'mikh-vasily'),
    ('test_role1', 'read_shop_test_eda', '2021-01-01 00:00:00', 'mikh-vasily'),
    ('test_role1', 'read_shop_test_lavka', '2021-01-01 00:00:00', 'mikh-vasily');

INSERT INTO agent.users_roles VALUES
    (1, '2021-01-01 00:00:00', 'mikh-vasily', 'test_role'),
    (2, '2021-01-01 00:00:00', 'test_user', 'test_role1');

INSERT INTO agent.goods (
    id,
    ru_name,
    en_name,
    type,
    created,
    creator,
    permission,
    ru_description,
    en_description,
    image_mds_id,
    visible
)
VALUES (
    1,
    'test_name',
    'test_name',
    'test_type',
    NOW(),
    'mikh-vasily',
    'read_shop_test_taxi',
    'test_description',
    'test_description',
    'test_image',
    true
);

INSERT INTO agent.goods_detail (
    id, goods_id, created, creator, price, ru_attribute,en_attribute, amount, visible
)
VALUES (1, 1, NOW(), 'mikh-vasily', 222.33, 'test_attr','test_attr', 2, true);

INSERT INTO agent.purchases (
    uid,
    created,
    updated,
    goods_detail_id,
    status_key,
    login,
    address_id,
    price,
    promocode_id
)
VALUES
(
    '1111',
    NOW(),
    NOW(),
    1,
    'purchase_init',
    'mikh-vasily',
    null,
    222.33,
    null
),
(
    '3333',
    NOW(),
    NOW(),
    1,
    'purchase_init',
    'webalex',
    null,
    222.33,
    null
);
