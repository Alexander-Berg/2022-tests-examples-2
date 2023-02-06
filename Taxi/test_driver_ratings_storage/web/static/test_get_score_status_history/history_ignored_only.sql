INSERT INTO driver_ratings_storage.driver_score_status_history
(order_id, is_ignored, login, source, description, event_at)
VALUES
('order_2', TRUE, 'login0', 'support', 'some_description', '2020-05-07 18:00:00.000000'),
('order_3', TRUE, 'login0', 'support', 'some_description', '2020-05-07 09:00:00.000000')
ON CONFLICT DO NOTHING
;
