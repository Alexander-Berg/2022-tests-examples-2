INSERT INTO driver_ratings_storage.drivers
  (driver_id, rating, created_at, updated_at, new_rating_calc_at)
VALUES
  ('driver_1', 1, '2019-05-01 00:00:00.000000', '2019-05-01 00:00:00.000000', NULL),
  ('driver_2', 2, '2019-05-01 00:00:00.000000', '2019-05-01 00:00:00.000000', NULL),
  ('driver_4', 4, '2019-05-01 00:00:00.000000', '2019-05-01 00:00:00.000000', NULL)
;

INSERT INTO driver_ratings_storage.scores
 (order_id, driver_id, score, scored_at)
VALUES
  ('order_1_1', 'driver_1', 1, '2019-05-01 00:00:00.000000'),
  ('order_1_2', 'driver_1', 1, '2019-05-02 00:00:00.000000'),
  ('order_2_1', 'driver_2', 2, '2019-05-03 00:00:00.000000'),
  ('order_2_2', 'driver_2', 2, '2019-05-04 00:00:00.000000'),
  ('order_3_1', 'driver_3', 3, '2019-05-05 00:00:00.000000'),
  ('order_3_2', 'driver_3', 3, '2019-05-06 00:00:00.000000'),
  ('order_4_1', 'driver_4', 4, '2019-05-07 00:00:00.000000'),
  ('order_4_2', 'driver_4', 4, '2019-05-08 00:00:00.000000')
;
