INSERT INTO eats_proactive_support.orders
(order_nr, status, promised_at, order_type, delivery_type, shipping_type, payload)
VALUES
    ('123', 'finished', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1", "created_at": "2020-04-28T11:00:00+03:00"}'),
    ('124', 'created', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "41", "application": "app2", "created_at": "2020-04-28T11:00:00+03:00"}'),
    ('125', 'confirmed', '2020-04-28T13:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app3", "created_at": "2020-04-28T11:00:00+03:00"}'),
    ('126', 'confirmed', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'pickup', '{"place_id": "40", "application": "app3", "created_at": "2020-04-28T11:00:00+03:00"}'),
    ('127', 'confirmed', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'marketplace', 'delivery', '{"place_id": "40", "application": "app3", "created_at": "2020-04-28T11:00:00+03:00"}'),
    ('128', 'taken', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1", "created_at": "2020-04-28T11:00:00+03:00"}'),
    ('129', 'confirmed', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1", "created_at": "2020-04-28T11:00:00+03:00"}'),
    ('130', 'confirmed', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1", "created_at": "2020-04-28T11:40:00+03:00"}');

INSERT INTO eats_proactive_support.orders_sensitive_data
(order_nr, eater_id, eater_personal_phone_id)
VALUES
    ('123', 'eater1', '+7-777-777-7777'),
    ('124', 'eater2', '+7-777-777-7777'),
    ('125', 'eater3', '+7-777-777-7778'),
    ('126', 'eater3', '+7-777-777-7778'),
    ('127', 'eater3', '+7-777-777-7778'),
    ('128', 'eater1', '+7-777-777-7777'),
    ('129', 'eater1', '+7-777-777-7777'),
    ('130', 'eater1', '+7-777-777-7777');
