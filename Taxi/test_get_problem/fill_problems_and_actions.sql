INSERT INTO eats_proactive_support.orders
(order_nr, status, promised_at, order_type, delivery_type, shipping_type, payload)
VALUES
('100000-100000', 'created', NOW(), 'dummy_order_type',
 'native', 'delivery', '{}'),
('100001-100000', 'created', NOW(), 'dummy_order_type',
 'native', 'delivery', '{}'),
('100011-100000', 'created', NOW(), 'dummy_order_type',
 'native', 'delivery', '{}');

INSERT INTO eats_proactive_support.problems
(id, order_nr, type)
VALUES ('873', '100000-100000', 'order_cancelled'),
       ('875', '100001-100000', 'order_cancelled');

INSERT INTO eats_proactive_support.actions
(id, external_id, problem_id, order_nr, type, payload, state)
VALUES ('123', '6d30f5fad3614664a881647a017c88b8', '873', '100000-100000', 'eater_notification',
        '{
        "notification_code": "dummy_event",
        "channels": ["sms", "push", "taxi_push"]
        }',
        'processing'),
        ('124', '4124.999-to.2413', '873', '100000-100000', 'eater_notification','{
         "notification_code": "dummy_event",
         "channels": ["sms", "push", "taxi_push"]
        }',
        'failed')
