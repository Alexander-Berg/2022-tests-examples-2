INSERT INTO driver_ratings_storage.drivers
  (driver_id, rating, new_rating_calc_at)
VALUES
  ('driver_1', NULL, NULL),
  ('driver_2', 3, '2019-05-10 00:00:00.000000')
;

INSERT INTO driver_ratings_storage.scores
 (order_id, driver_id, score, scored_at)
VALUES
  ('order_1_1', 'driver_1', 5, '2019-05-01 00:00:00.000000'),
  ('order_2_1', 'driver_1', 5, '2019-05-02 00:00:00.000000'),
  ('order_3_1', 'driver_1', 5, '2019-05-03 00:00:00.000000'),
  ('order_4_1', 'driver_1', 5, '2019-05-04 00:00:00.000000'),
  ('order_5_1', 'driver_1', 5, '2019-05-05 00:00:00.000000'),
  ('order_6_1', 'driver_1', 4, '2019-05-06 00:00:00.000000'),
  ('order_7_1', 'driver_1', 4, '2019-05-07 00:00:00.000000'),
  ('order_8_1', 'driver_1', 4, '2019-05-08 00:00:00.000000'),
  ('order_9_1', 'driver_1', 4, '2019-05-09 00:00:00.000000'),
  ('order_10_1', 'driver_1', 4, '2019-05-10 00:00:00.000000'),
  ('order_11_1', 'driver_1', 3, '2019-05-11 00:00:00.000000'),
  ('order_12_1', 'driver_1', 3, '2019-05-12 00:00:00.000000'),
  ('order_13_1', 'driver_1', 3, '2019-05-13 00:00:00.000000'),
  ('order_14_1', 'driver_1', 3, '2019-05-14 00:00:00.000000'),
  ('order_15_1', 'driver_1', 3, '2019-05-15 00:00:00.000000'),
  ('order_1_2', 'driver_2', 3, '2019-05-09 00:00:00.000000')
;


INSERT INTO driver_ratings_storage.driver_scores
 (order_id, park_id, driver_profile_id, score, scored_at)
VALUES
  ('order_1_1',  'park_1', 'driver_1', 5, '2019-05-01 00:00:00.000000'),
  ('order_2_1',  'park_1', 'driver_1', 5, '2019-05-02 00:00:00.000000'),
  ('order_3_1',  'park_1', 'driver_1', 5, '2019-05-03 00:00:00.000000'),
  ('order_4_1',  'park_1', 'driver_1', 5, '2019-05-04 00:00:00.000000'),
  ('order_5_1',  'park_1', 'driver_1', 5, '2019-05-05 00:00:00.000000'),
  ('order_6_1',  'park_1', 'driver_1', 4, '2019-05-06 00:00:00.000000'),
  ('order_7_1',  'park_1', 'driver_1', 4, '2019-05-07 00:00:00.000000'),
  ('order_8_1',  'park_1', 'driver_2', 4, '2019-05-08 00:00:00.000000'),
  ('order_9_1',  'park_1', 'driver_2', 4, '2019-05-09 00:00:00.000000'),
  ('order_10_1', 'park_1', 'driver_2', 4, '2019-05-10 00:00:00.000000'),
  ('order_11_1', 'park_1', 'driver_2', 3, '2019-05-11 00:00:00.000000'),
  ('order_12_1', 'park_1', 'driver_2', 3, '2019-05-12 00:00:00.000000'),
  ('order_13_1', 'park_1', 'driver_2', 3, '2019-05-13 00:00:00.000000'),
  ('order_14_1', 'park_1', 'driver_2', 3, '2019-05-14 00:00:00.000000'),
  ('order_15_1', 'park_1', 'driver_2', 3, '2019-05-15 00:00:00.000000'),
  ('order_1_2',  'park_1', 'driver_3', 3, '2019-05-09 00:00:00.000000')
;
