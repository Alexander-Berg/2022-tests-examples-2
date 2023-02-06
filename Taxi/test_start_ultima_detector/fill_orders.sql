INSERT INTO eats_proactive_support.orders
(order_nr, status, promised_at, order_type, delivery_type, shipping_type, payload)
VALUES
    ('123', 'created', NOW(), 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1", "delivery_class":"ultima"}'),
    ('124', 'payed', NOW(), 'dummy_order_type',
     'native', 'delivery', '{"place_id": "41", "application": "app2", "delivery_class":"ultima"}'),
    ('125', 'created', NOW(), 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app3", "delivery_class":"ultima"}'),
    ('126', 'created', NOW(), 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1", "delivery_class":"regular"}');

INSERT INTO eats_proactive_support.orders_sensitive_data
(order_nr, eater_id, eater_personal_phone_id, eater_device_id)
VALUES
    ('123', 'eater1', '+7-777-777-7777', 'some_device_id'),
    ('124', 'eater2', '+7-777-777-7777', 'some_device_id'),
    ('125', 'eater3', '+7-777-777-7778', 'some_device_id'),
    ('126', 'eater1', '+7-777-777-7777', 'some_device_id');
