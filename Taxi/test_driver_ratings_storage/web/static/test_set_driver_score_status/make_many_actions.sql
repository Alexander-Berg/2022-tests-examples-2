INSERT INTO driver_ratings_storage.driver_score_status_history
(order_id, is_ignored, login, source, description)
VALUES
('order_1', TRUE, 'login', 'support', 'some_description'),
('order_2', TRUE, 'login', 'support', 'some_description'),
('order_3', TRUE, 'login', 'support', 'some_description'),
('order_4', TRUE, 'login', 'support', 'some_description'),
('order_5', TRUE, 'login', 'support', 'some_description'),
('order_6', TRUE, 'login', 'support', 'some_description')
ON CONFLICT DO NOTHING
;
