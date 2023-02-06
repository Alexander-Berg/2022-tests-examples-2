INSERT INTO driver_ratings_storage.driver_score_status_history
(order_id, is_ignored, login, source, description)
VALUES
('some_order_id', FALSE, 'another_login', 'support', 'another_description')
ON CONFLICT DO NOTHING
;
