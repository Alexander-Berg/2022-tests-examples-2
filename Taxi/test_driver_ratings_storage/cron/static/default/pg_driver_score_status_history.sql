INSERT INTO driver_ratings_storage.scores
 (order_id, driver_id, score, scored_at, ignore_started_at)
VALUES
  ('order_7_1', 'driver_2', 5, '2019-05-14 00:00:00.000000', NULL),
  ('order_7_2', 'driver_2', 5, '2019-05-14 00:00:00.000000', NULL),
  ('order_7_3', 'driver_2', 5, '2019-05-14 00:00:00.000000', NULL)
;

INSERT INTO driver_ratings_storage.driver_score_status_history
  (order_id, source, login, is_ignored, description, event_at)
VALUES
  ('order_7_1', 'support', 'ivan', TRUE, 'Ivans description', '2019-08-15 15:00:00'::TIMESTAMP  AT TIME ZONE 'UTC'),

  ('order_7_2', 'support', 'ivan', TRUE, 'Petrs description', '2019-08-15 15:00:00'::TIMESTAMP  AT TIME ZONE 'UTC'),
  ('order_7_2', 'support', 'petr', FALSE, 'Alexs description', '2019-08-15 16:00:00'::TIMESTAMP  AT TIME ZONE 'UTC'),

  ('order_7_3', 'support', 'ivan', TRUE, 'Ivans description', '2019-08-15 15:00:00'::TIMESTAMP  AT TIME ZONE 'UTC'),
  ('order_7_3', 'support', 'petr', FALSE, 'Petrs description', '2019-08-15 16:00:00'::TIMESTAMP  AT TIME ZONE 'UTC'),
  ('order_7_3', 'support', 'alex', TRUE, 'Alexs description', '2019-08-15 17:00:00'::TIMESTAMP  AT TIME ZONE 'UTC'),

  -- it is ignored
  ('order_3_2', 'support', 'abcd', FALSE, 'Abcds description', '2019-08-15 15:00:00'::TIMESTAMP  AT TIME ZONE 'UTC'),

  -- it is also ignored, by event_at is too far in the past
  ('order_2_2', 'support', 'abcd', FALSE, 'Abcds description', '2019-01-01 00:00:00'::TIMESTAMP  AT TIME ZONE 'UTC')
;
