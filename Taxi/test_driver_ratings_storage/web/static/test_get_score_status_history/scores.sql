INSERT INTO driver_ratings_storage.scores
  (order_id, driver_id, score, scored_at, ignore_started_at)
VALUES
  ('order_1', 'driver_1', 5, '2020-05-08 00:00:00.000000', NULL),
  ('order_2', 'driver_1', 5, '2020-05-07 12:00:00.000000', '2020-05-07 18:00:00.000000'),
  ('order_3', 'driver_1', 5, '2020-05-07 00:00:00.000000', '2020-05-07 09:00:00.000000'),
  ('order_4', 'driver_1', 5, '2020-05-06 12:00:00.000000', NULL),
  ('order_5', 'driver_1', 5, '2020-05-06 00:00:00.000000', NULL),

  ('order_6', 'driver_1', 5, '2020-05-05 00:00:01.000000', NULL),
  ('order_7', 'driver_1', 5, '2020-05-05 00:00:00.000000', '2020-05-07 22:00:00.000000')
;
