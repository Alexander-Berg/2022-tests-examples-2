INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at
)
VALUES
    (1120000000252888, NOW(), 'admin', 'admin', 'admin', '2022-01-01');

INSERT INTO agent.permissions VALUES
    ('read_shop_test_taxi', NOW(), NOW(), 'admin', 'test', 'test', 'test', 'test'),
    ('write_admin_shop', NOW(), NOW(), 'admin', 'test', 'test', 'test', 'test');


INSERT INTO agent.roles VALUES
    ('test_role', NOW(), NOW(), 'admin', 'тест', 'test', 'тест', 'test');

INSERT INTO agent.roles_permissions VALUES
    ('test_role', 'read_shop_test_taxi', '2021-01-01 00:00:00', 'admin'),
    ('test_role', 'write_admin_shop', '2021-01-01 00:00:00', 'admin');

INSERT INTO agent.users_roles VALUES
    (1, '2021-01-01 00:00:00', 'admin', 'test_role');


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
    'admin',
    'read_shop_test_taxi',
    'test_description',
    'test_description',
    'test_image',
    true
);


INSERT INTO agent.goods_detail (
    id,
    goods_id,
    created,
    creator,
    price,
    ru_attribute,
    en_attribute,
    amount,
    visible
)
VALUES
(1, 1, NOW(), 'admin', 222.33, 'test_attr','test_attr', 52, true);

