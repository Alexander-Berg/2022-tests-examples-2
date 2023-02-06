INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at
)
VALUES
    (1120000000252888, NOW(), 'mikh-vasily', 'Тест', 'Тестовый', '2016-06-02'),
    (1120000000252889, NOW(), 'webalex', 'Тест1', 'Тестовый1', '2016-06-02');

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
);

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
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
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
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    '222333',
    'ru',
    'Москва',
    'Кривая',
    '1',
    'test_build',
    'test_flat',
    'mikh-vasily'
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
),
(
    '5555',
    'test_doc5',
    NOW(),
    'mikh-vasily',
    'test_taxi_project',
    222.33,
    'charge_payment',
    'shop',
    'payment',
    False
);

INSERT INTO agent.purchases (
    uid,
    created,
    updated,
    goods_detail_id,
    status_key,
    login,
    address_id,
    price,
    promocode_id,
    billing_operations_history_id

)
VALUES
    ('1111', '2021-01-01 00:00:05+0', NOW(),  1, 'purchase_init', 'mikh-vasily', 1, 222.33, null, null),
    ('2222', '2021-01-01 00:00:04+0', NOW(), 1, 'purchase_successfull', 'mikh-vasily', 2, 222.33, null, '2222'),
    ('3333', '2021-01-01 00:00:03+0', NOW(), 1, 'purchase_not_enough_subproduct', 'webalex', null, 222.33, null, null),
    ('4444', '2021-01-01 00:00:02+0', NOW(), 2, 'purchase_not_enough_coins', 'webalex', null, 333.33, 1, '4444'),
    ('5555', '2021-01-01 00:00:01+0', NOW(), 1, 'billing_error', 'mikh-vasily', null, 222.33, null, '5555'),
    ('6666', '2021-01-01 00:00:01+0', NOW(), 1, 'purchase_reserved', 'mikh-vasily', null, 222.33, 1, '5555'),
    ('7777', '2021-01-01 00:00:01+0', NOW(), 1, 'purchase_successfull', 'mikh-vasily', null, 222.33, null, '5555');
