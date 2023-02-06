INSERT INTO driver_ratings_storage.driver_score_status_history
(order_id, is_ignored, login, source, description)
VALUES
('some_order_id', TRUE, 'some_login', 'support', 'some_description')
ON CONFLICT DO NOTHING
;
