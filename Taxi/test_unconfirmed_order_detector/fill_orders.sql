INSERT INTO eats_proactive_support.orders
(order_nr, status, promised_at, sent_at, order_type, delivery_type, shipping_type, payload)
VALUES
    ('123', 'created', NOW(), NULL, 'dummy_order_type',
     'native', 'delivery',
     '{"application": "android", "place_id": "40"}'),
    ('124', 'confirmed', NOW(), NULL, 'dummy_order_type',
     'native', 'delivery',
     '{"application": "android", "place_id": "40"}'),
    ('130', 'created', NOW(), '2021-09-09T09:59:59+03:00', 'dummy_order_type',
     'native', 'delivery',
     '{"application": "android", "place_id": "40"}'),
    ('131', 'confirmed', NOW(), '2021-09-09T09:59:59+03:00', 'dummy_order_type',
     'native', 'delivery',
     '{"application": "android", "place_id": "40"}'),
    ('132', 'created', NOW(), '2021-09-09T10:00:01+03:00', 'dummy_order_type',
     'native', 'delivery',
     '{"application": "android", "place_id": "40"}'),
    ('133', 'confirmed', NOW(), '2021-09-09T10:00:01+03:00', 'dummy_order_type',
     'native', 'delivery',
     '{"application": "android", "place_id": "40"}');

INSERT INTO eats_proactive_support.orders_sensitive_data
(order_nr, eater_id, eater_personal_phone_id)
VALUES
    ('123', 'eater1', '+7-777-777-7777'),
    ('124', 'eater1', '+7-777-777-7777'),
    ('130', 'eater1', '+7-777-777-7777'),
    ('131', 'eater1', '+7-777-777-7777'),
    ('132', 'eater1', '+7-777-777-7777'),
    ('133', 'eater1', '+7-777-777-7777');
