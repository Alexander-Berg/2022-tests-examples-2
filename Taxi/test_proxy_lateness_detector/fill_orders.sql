INSERT INTO eats_proactive_support.orders
(order_nr, status, promised_at, order_type, delivery_type, shipping_type, payload)
VALUES
    ('123', 'created', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1"}'),
    ('124', 'payed', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "41", "application": "app2"}'),
    ('125', 'payed', '2020-04-28T12:00:00+03:00', 'retail',
     'native', 'delivery', '{"place_id": "41", "application": "app2"}');

INSERT INTO eats_proactive_support.orders_sensitive_data
(order_nr, eater_id, eater_personal_phone_id)
VALUES
    ('123', 'eater1', '+7-777-777-7777'),
    ('124', 'eater1', '+7-777-777-7777'),
    ('125', 'eater1', '+7-777-777-7777');
