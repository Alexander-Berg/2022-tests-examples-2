INSERT INTO sber_int_api.claims (
        external_id,
        taxi_order_id,
        status,
        personal_phone_id,
        route,
        created_at,
        updated_at
    )
VALUES (
    'e1',
    'order_id_1',
    'pending',
    'defee2e75b2039c74d9cfbc068d0aef7',
    '["Москва, улица Вавилова, 19", "Москва, Кутузовский проспект, 32"]',
    '2019-08-18 15:30:27'::timestamp,
    '2019-08-18 15:30:27'::timestamp
);
