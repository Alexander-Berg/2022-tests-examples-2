INSERT INTO eats_proactive_support.orders
(order_nr, status, promised_at, order_type, delivery_type, shipping_type, payload)
VALUES
    ('123', 'created', NOW(), 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1"}'),
    ('126', 'created', NOW(), 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1"}');

INSERT INTO eats_proactive_support.orders_sensitive_data
(order_nr, eater_id, eater_personal_phone_id, eater_device_id)
VALUES
    ('123', 'eater1', '+7-777-777-7777', 'some_wrong_device_id'),
    ('126', 'eater1', '+8-888-888-8888', 'some_device_id');
