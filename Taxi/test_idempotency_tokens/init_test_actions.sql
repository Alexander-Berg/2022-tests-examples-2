INSERT INTO eats_proactive_support.orders
(order_nr, status, promised_at, order_type, delivery_type, shipping_type, payload)
VALUES
    ('111111-111111', 'cancelled', '2020-01-01T00:00:00+03:00',
     'dummy_order_type', 'native', 'delivery',
     '{"place_id": "40", "application": "app1"}');


INSERT INTO eats_proactive_support.orders_sensitive_data
(order_nr, eater_id, eater_personal_phone_id)
VALUES
    ('111111-111111', 'eater1', 'phone_id_1');


INSERT INTO eats_proactive_support.problems
(id, order_nr, type)
VALUES ('1000', '111111-111111', 'order_cancelled');


INSERT INTO eats_proactive_support.actions
(id, problem_id, order_nr, type, payload, state)
VALUES ('100', '1000', '111111-111111', 'eater_notification',
        '{
        "notification_code": "dummy_event",
        "channels": ["push"]
        }',
        'created'),
       ('101', '1000', '111111-111111', 'eater_robocall',
        '{
         "delay_sec": 0,
         "voice_line": "dummy_voice_line"
        }',
        'created');
