INSERT INTO eats_proactive_support.orders
(order_nr, status, promised_at, order_type, delivery_type, shipping_type, payload)
VALUES
    ('123', 'finished', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1"}'),
    ('124', 'finished', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "40", "application": "app1"}'),
    ('125', 'finished', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'native', 'delivery', '{"place_id": "50", "application": "app1"}'),
    ('126', 'finished', '2020-04-28T12:00:00+03:00', 'dummy_order_type',
     'marketplace', 'delivery', '{"place_id": "50", "application": "app1"}');

INSERT INTO eats_proactive_support.orders_sensitive_data
(order_nr, eater_id, eater_personal_phone_id)
VALUES
    ('123', 'eater1', '+7-777-777-7777'),
    ('124', 'eater2', '+7-777-777-7777'),
    ('125', 'eater3', '+7-777-777-7777'),
    ('126', 'eater3', '+7-777-777-7777');

INSERT INTO eats_proactive_support.problems
(id, order_nr, type)
VALUES ('873', '124', 'lateness'),
       ('875', '125', 'lateness'),
       ('876', '126', 'lateness');
