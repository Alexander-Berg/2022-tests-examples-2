INSERT INTO eats_proactive_support.orders
(order_nr, status, promised_at, order_type, delivery_type, shipping_type, payload)
VALUES
    ('123', 'created', NOW(), 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1"}'),
    ('124', 'finished', NOW(), 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1"}'),
    ('125', 'created', NOW(), 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1"}'),
    ('126', 'created', NOW(), 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1"}'),
    ('127', 'created', NOW(), 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1"}'),
    ('128', 'created', NOW(), 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1"}');

INSERT INTO eats_proactive_support.orders_sensitive_data
(order_nr, eater_id, eater_personal_phone_id)
VALUES
    ('123', 'eater1', 'phone_id_1'),
    ('124', 'eater1', 'phone_id_1'),
    ('125', 'eater1', 'phone_id_1'),
    ('126', 'eater1', 'phone_id_1'),
    ('127', 'eater1', 'phone_id_1'),
    ('128', 'eater1', 'phone_id_1');
