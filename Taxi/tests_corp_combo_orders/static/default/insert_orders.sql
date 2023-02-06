INSERT INTO corp_combo_orders.deliveries (
    id,
    client_id,
    route_type,
    common_point
) VALUES (
    'e98858cbd7784d7689e2635728334138',
    'client_id_1',
    'ONE_A_MANY_B',
    '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }'
);

INSERT INTO corp_combo_orders.orders (
    id,
    delivery_id,
    personal_phone_id,
    source,
    destination,
    interim_destinations,
    status,
    taxi_status,
    version
) VALUES (
    'test_order_id',
    'e98858cbd7784d7689e2635728334138',
    'per_1',
    '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }',
    '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }',
    '{}',
    'pending',
    '',
    9
),
(
    'test_order_id_2',
    'e98858cbd7784d7689e2635728334138',
    'per_1',
    '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }',
    '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }',
    '{}',
    'assigned',
    'driving',
    9
);

INSERT INTO corp_combo_orders.order_points (
    order_id,
    user_personal_phone_id,
    point
) VALUES (
    'test_order_id',
    'per_1',
    '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }'
),
(
    'test_order_id',
    'per_2',
    '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }'
),
(
    'test_order_id',
    'per_3',
    '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }'
),
(
    'test_order_id_2',
    'per_2',
    '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }'
);
