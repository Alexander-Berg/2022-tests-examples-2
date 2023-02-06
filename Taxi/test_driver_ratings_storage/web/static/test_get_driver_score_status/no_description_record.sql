INSERT INTO driver_ratings_storage.driver_score_status_history
  (order_id, is_ignored, login, source, description)
VALUES
  ('some_order_id', TRUE, 'yet_another_login', 'script', 'Analytics script')
ON CONFLICT DO NOTHING
;
