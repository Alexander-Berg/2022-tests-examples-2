INSERT INTO eats_proactive_support.actions
(id, external_id, problem_id, order_nr, type, payload, state, updated_at)
VALUES
('125', '6d30f5fad3614664a881647a017c88b8', '875', '100000-100011', 'eater_notification',
'{"notification_code": "dummy_event","channels": ["sms", "push", "taxi_push"]}',
'processing', '2021-12-01T12:00:00.1234+03:00'::TIMESTAMPTZ),
('126', '6d30f5fad3614664a881647a017c88b8', '876', '100000-100111', 'eater_notification',
'{"notification_code": "dummy_event","channels": ["sms", "push", "taxi_push"]}',
'processing', '2021-12-12T12:00:00.1234+03:00'::TIMESTAMPTZ);
