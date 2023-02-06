INSERT INTO eats_proactive_support.orders
(order_nr, status, promised_at, order_type, delivery_type, shipping_type, payload)
VALUES
    ('128', 'taken', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1", "created_at": "2020-04-28T11:00:00+03:00"}'),
    ('129', 'taken', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1", "created_at": "2020-04-28T11:00:00+03:00"}');

INSERT INTO eats_proactive_support.orders_sensitive_data
(order_nr, eater_id, eater_personal_phone_id)
VALUES
    ('128', 'eater1', '+7-777-777-7777'),
    ('129', 'eater1', '+7-777-777-7777');
