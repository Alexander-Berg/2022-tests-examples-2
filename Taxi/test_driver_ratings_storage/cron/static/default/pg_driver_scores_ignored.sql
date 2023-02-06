INSERT INTO driver_ratings_storage.drivers
  (driver_id, updated_at)
VALUES
  ('driver_2', '2019-05-14 00:00:00.000000')
;

INSERT INTO driver_ratings_storage.scores
 (order_id, driver_id, score, scored_at, ignore_started_at)
VALUES
  ('order_1_2', 'driver_2', 5, '2019-05-14 00:00:00.000000', NULL),
  ('order_2_2', 'driver_2', 5, '2019-05-15 00:00:00.000000', NULL),
  ('order_3_2', 'driver_2', 1, '2019-05-14 00:00:00.000000', '2019-05-14 15:00:00.000000'),
  ('order_4_2', 'driver_2', 1, '2019-05-15 00:00:00.000000', '2019-05-14 15:00:00.000000'),
  ('order_5_2', 'driver_2', 5, '2019-05-14 00:00:00.000000', NULL),
  ('order_6_2', 'driver_2', 5, '2019-05-15 00:00:00.000000', NULL)
;

INSERT INTO common.events(task_id, name, created_at, details)
VALUES ('111111111111', 'load_ignored_scores', '2019-04-13 15:00:00.000000', '{"uploaded_at": "2019-04-13 15:00:00.000000+00:00"}'::JSONB),
       ('222222222222', 'load_ignored_scores', '2019-05-14 15:00:00.000000', '{"uploaded_at": "2019-05-14 15:00:00.000000+00:00"}'::JSONB)
;
