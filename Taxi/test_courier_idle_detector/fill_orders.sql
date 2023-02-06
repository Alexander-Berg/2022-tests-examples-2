INSERT INTO eats_proactive_support.orders
(order_nr, status, promised_at, order_type, delivery_type, shipping_type, payload)
VALUES
    ('123', 'confirmed', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1", "taken_at": "2020-04-28T11:00:00+03:00"}'),
    ('124', 'confirmed', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "41", "application": "app2", "taken_at": "2020-04-28T11:00:00+03:00"}'),
    ('125', 'finished', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "41", "application": "app2", "taken_at": "2020-04-28T11:00:00+03:00"}'),
    ('126', 'confirmed', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "41", "application": "app2", "taken_at": "2020-04-28T11:00:00+03:00"}'),
    ('127', 'confirmed', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "41", "application": "app2", "taken_at": "2020-04-28T11:00:00+03:00"}'),
    ('130', 'taken', '2020-04-27T10:00:00+03:00', 'dummy_order_type',
    'native', 'delivery', '{"place_id": "41", "application": "app2", "taken_at": "2020-04-28T11:00:00+03:00"}');

INSERT INTO eats_proactive_support.orders
(order_nr, status, promised_at, order_type, delivery_type, shipping_type, park_id, driver_id, payload)
VALUES
    ('128', 'finished', '2020-04-28T12:00:00+03:00', 'dummy_order_type', 'native', 'delivery',
     'park_id126', 'driver_id126', '{"place_id": "41", "application": "app2", "taken_at": "2020-04-28T11:00:00+03:00"}'),
    ('129', 'taken', '2020-04-28T12:00:00+03:00', 'dummy_order_type', 'native', 'delivery',
     'park_id127', 'driver_id127', '{"place_id": "41", "application": "app2", "taken_at": "2020-04-28T11:00:00+03:00"}');

INSERT INTO eats_proactive_support.orders_sensitive_data
(order_nr, eater_id, eater_personal_phone_id, eater_device_id)
VALUES
    ('123', 'eater1', '+7-777-777-7777', 'some_device_id'),
    ('124', 'eater2', '+7-777-777-7777', 'detector_off'),
    ('125', 'eater2', '+7-777-777-7777', 'some_device_id'),
    ('126', 'eater2', '+7-777-777-7777', 'some_device_id'),
    ('127', 'eater2', '+7-777-777-7777', 'some_device_id'),
    ('128', 'eater2', '+7-777-777-7777', 'some_device_id'),
    ('129', 'eater2', '+7-777-777-7777', 'some_device_id'),
    ('130', 'eater2', '+7-777-777-7777', 'some_device_id');
