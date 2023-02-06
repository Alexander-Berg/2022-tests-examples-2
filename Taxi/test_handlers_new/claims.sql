INSERT INTO sber_int_api.claims (
        external_id,
        taxi_order_id,
        status,
        close_status,
        personal_phone_id,
        route,
        created_at,
        updated_at
    )
VALUES (
    'new',
    null,
    'new',
    null,
    'defee2e75b2039c74d9cfbc068d0aef7',
    '["Москва, улица Вавилова, 19", "Москва, Кутузовский проспект, 32"]',
    '2019-08-18 15:30:27'::timestamp,
    '2019-08-18 15:30:27'::timestamp
),
(
    'draft',
    'order_id_2',
    'draft',
    null,
    'defee2e75b2039c74d9cfbc068d0aef7',
    '["Москва, улица Вавилова, 19", "Москва, Кутузовский проспект, 32"]',
    '2019-08-18 15:30:27'::timestamp,
    '2019-08-18 15:30:27'::timestamp
),
(
    'pending',
    'order_id_3',
    'pending',
    null,
    'defee2e75b2039c74d9cfbc068d0aef7',
    '["Москва, улица Вавилова, 19", "Москва, Кутузовский проспект, 32"]',
    '2019-08-18 15:30:27'::timestamp,
    '2019-08-18 15:30:27'::timestamp
),
(
    'complete',
    'order_id_4',
    'complete',
    'complete',
    'defee2e75b2039c74d9cfbc068d0aef7',
    '["Москва, улица Вавилова, 19", "Москва, Кутузовский проспект, 32"]',
    '2019-08-18 15:30:27'::timestamp,
    '2019-08-18 15:30:27'::timestamp
);
