INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at
)
VALUES
    (11200000002528, NOW(), 'mikh-vasily', 'Тест', 'Тестовый', '2016-06-02'),
    (11200000002528, NOW(), 'webalex', 'Тест1', 'Тестовый1', '2016-06-02');

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
    'read_admin_shop',
    NOW(),
    NOW(),
    'mikh-vasily',
    'test3',
    'test3',
    'test3',
    'test3'
);

INSERT INTO agent.roles VALUES
    ('test_role', NOW(), NOW(), 'mikh-vasily', 'тест', 'test', 'тест', 'test');

INSERT INTO agent.roles_permissions VALUES
    ('test_role', 'read_admin_shop', '2021-01-01 00:00:00', 'mikh-vasily');

INSERT INTO agent.users_roles VALUES
    (1, '2021-01-01 00:00:00', 'mikh-vasily', 'test_role');

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
),
(
    2,
    'test_promo',
    'test_promo',
    'promocode',
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
VALUES
       (1, 1, NOW(), 'mikh-vasily', 222.33, 'test_attr','test_attr', 2, true),
       (2, 2, NOW(), 'mikh-vasily', 333.33, 'test_attr1','test_attr1', 2, true);

INSERT INTO agent.promocodes (
    id, created, updated, hash, goods_detail_id, used
)
VALUES
    (1, NOW(), '2021-02-03T00:00:00+0', 'test_hash', 2, true),
    (2, NOW(), '2021-02-03T00:00:00+0', 'test_hash1', 2, false);

INSERT INTO agent.addresses (
    type,
    created,
    updated,
    postcode,
    country,
    city,
    street,
    house,
    building,
    flat,
    login
) VALUES (
    'user',
    '2021-01-01 00:00:00+0',
    '2021-01-01 00:00:00+0',
    '222333',
    'ru',
    'Москва',
    'Кривая',
    '1',
    null,
    null,
    'mikh-vasily'
),
(
    'user',
    '2021-01-01 00:00:00+0',
    '2021-01-01 00:00:00+0',
    '222333',
    'ru',
    'Москва',
    'Кривая',
    '1',
    'test_build',
    'test_flat',
    null
);

INSERT INTO agent.billing_operations_history(
    id,
    doc_id,
    dt,
    login,
    project,
    value,
    operation_type,
    section_type,
    description,
    viewed
)
VALUES (
    '2222',
    'test_doc',
    NOW(),
    'mikh-vasily',
    'test_taxi_project',
    222.33,
    'charge_payment',
    'shop',
    'payment',
    False
),
(
    '4444',
    'test_doc4',
    NOW(),
    'webalex',
    'test_taxi_project',
    333.33,
    'charge_payment',
    'shop',
    'payment',
    False
);

INSERT INTO agent.purchases (
    uid,
    created,
    updated,
    billing_operations_history_id,
    goods_detail_id,
    status_key,
    login,
    address_id,
    price,
    promocode_id
)
VALUES (
    '1111',
    '2021-01-01 00:00:04+0',
    '2021-01-01 00:00:04+0',
    null,
    1,
    'purchase_init',
    'mikh-vasily',
    1,
    222.33,
    null
),
(
    '2222',
    '2021-01-01 00:00:03+0',
    '2021-01-01 00:00:03+0',
    '2222',
    1,
    'purchase_successfull',
    'mikh-vasily',
    2,
    222.33,
    null
),
(
    '3333',
    '2021-01-01 00:00:02+0',
    '2021-01-01 00:00:02+0',
    null,
    1,
    'purchase_not_enough_subproduct',
    'webalex',
    null,
    222.33,
    null
),
(
    '4444',
    '2021-01-01 00:00:01+0',
    '2021-01-01 00:00:01+0',
    '4444',
    2,
    'purchase_successfull',
    'webalex',
    null,
    333.33,
    1
);
