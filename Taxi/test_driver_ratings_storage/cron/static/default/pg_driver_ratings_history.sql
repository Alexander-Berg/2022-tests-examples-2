INSERT INTO driver_ratings_storage.drivers
  (driver_id, rating, new_rating_calc_at)
VALUES
  ('driver1', 3, '2019-05-10 00:00:00.000000'),
  ('driver2', 3, '2019-05-10 00:00:00.000000'),
  ('driver3', 3, '2019-05-10 00:00:00.000000')
;


INSERT INTO driver_ratings_storage.ratings_history (driver_id, calc_at, rating)
VALUES
('driver1','2020-10-02 17:36:41.011629+00', 1),
('driver2','2020-10-02 17:48:01.755559+00', 1),
('driver1','2020-10-03 15:37:09.060651+00', 2),
('driver2','2020-10-03 15:48:33.931281+00', 2),
('driver1','2020-10-05 16:01:59.266779+00', 3),
('driver2','2020-10-05 16:13:46.843113+00', 3),
('driver1','2020-10-06 01:11:45.853361+00', 4),
('driver2','2020-10-06 01:23:21.204324+00', 4),
('driver3','2020-10-07 04:22:12.412324+00', 4);
