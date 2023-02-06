INSERT INTO driver_ratings_storage.driver_score_status_history
(order_id, is_ignored, login, source, description, event_at)
VALUES
('order_2', TRUE, 'login0', 'support', 'some_description', '2020-05-07 18:00:00.000000'),
('order_3', TRUE, 'login0', 'support', 'some_description', '2020-05-07 09:00:00.000000'),

('order_3', FALSE, 'login', 'support', 'some_description', '2020-05-07 10:00:00.000000'), -- restore

('order_4', TRUE, 'login0', 'support', 'some_description', '2020-05-06 15:00:00.000000'),

('order_5', TRUE, 'login0', 'support', 'some_description', '2020-05-06 05:00:00.000000'),
('order_5', FALSE, 'login', 'support', 'some_description', '2020-05-06 05:01:00.000000'),
('order_5', TRUE, 'login0', 'support', 'some_description', '2020-05-07 12:00:00.000000')
ON CONFLICT DO NOTHING
;
