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
    'test_name1',
    'test_name1',
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
    id, goods_id, created, updated, creator, price, ru_attribute,en_attribute, amount, visible
)
VALUES
       (1, 1, NOW(), '2021-02-03T00:00:00+0', 'mikh-vasily', 222.33, 'test_attr','test_attr', 2, true),
       (2, 1, NOW(), '2021-02-03T00:00:00+0', 'mikh-vasily', 333.33, 'test_attr','test_attr', 0, true),
       (3, 2, NOW(), '2021-02-03T00:00:00+0', 'mikh-vasily', 222.11, 'test_attr2','test_attr2', 3, true);

INSERT INTO agent.promocodes (
    id, created, updated, hash, goods_detail_id, used
)
VALUES
    (1, NOW(), '2021-02-03T00:00:00+0', 'test_hash', 3, false),
    (2, NOW(), '2021-02-03T00:00:00+0', 'test_hash1', 3, false),
    (3, NOW(), '2021-02-03T00:00:00+0', 'test_hash2', 3, true);

INSERT INTO agent.addresses (
    type, created, updated, postcode, country, city, street, house, login
) VALUES (
    'user',
    '2021-01-01 00:00:00',
    '2021-01-01 00:00:00',
    '222333',
    'ru',
    'Москва',
    'Кривая',
    '1',
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
    '222',
    'test_doc',
    '2021-02-03T00:00:00+0',
    'mikh-vasily',
    'test_taxi_project',
    222.33,
    'payment_charge',
    'shop',
    'Purchase',
    False
),
(
    '444',
    'test_doc4',
    '2021-02-03T00:00:00+0',
    'webalex',
    'test_taxi_project',
    333.33,
    'payment_charge',
    'shop',
    'Purchase',
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
    ('111', '2020-12-31 21:00:00+0', NOW(),  3, 'purchase_init', 'mikh-vasily', null, 222.33, null, null),
    ('222', '2020-12-31 21:00:00+0', NOW(), 3, 'purchase_successfull', 'mikh-vasily', null, 222.33, 3, '222'),
    ('333', '2020-12-31 21:00:00+0', NOW(), 3, 'purchase_not_enough_subproduct', 'mikh-vasily', null, 222.33, null, null),
    ('444', '2020-12-31 21:00:00+0', NOW(), 3, 'purchase_not_enough_coins', 'mikh-vasily', null, 222.33, null, null),
    ('555', '2020-12-31 21:00:00+0', NOW(), 3, 'billing_error', 'mikh-vasily', null, 222.11, null, null),
    ('666', '2020-12-31 21:00:00+0', NOW(), 3, 'purchase_reserved', 'mikh-vasily', null, 222.11, 3, null);
