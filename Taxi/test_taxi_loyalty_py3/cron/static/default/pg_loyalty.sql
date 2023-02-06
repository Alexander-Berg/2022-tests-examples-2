INSERT INTO loyalty.loyalty_accounts
  (id, unique_driver_id, next_recount, status)
VALUES
  ('1', 'driver11', '2019-05-01 03:00:00.000000', 'newbie'),
  ('2', 'driver12', '2019-05-01 03:00:00.000000', 'newbie'),
  ('3', 'driver13', '2019-05-01 03:00:00.000000', 'newbie'),
  ('4', 'driver14', '2019-05-01 03:00:00.000000', 'bronze'),
  ('5', 'driver15', '2019-05-01 03:00:00.000000', 'returnee'),
  ('6', 'driver16', '2019-05-01 03:00:00.000000', 'newbie');

INSERT INTO loyalty.status_logs
 (created, status, unique_driver_id, reason, points)
VALUES
  ('2019-04-14 02:19:00.000000', 'gold', 'driver0', 'registration', 0),
  ('2019-04-14 02:20:00.000000', 'bronze', 'driver1', 'registration', 1),
  ('2019-04-14 02:23:00.000000', 'silver', 'driver2', 'other', 2),
  ('2019-04-14 02:24:30.000000', 'bronze', 'driver3', 'registration', 3),
  ('2019-04-14 02:23:00.000000', 'gold', 'driver4', 'registration', 4),
  ('2019-04-14 02:22:00.000000', 'bronze', 'driver5', 'other', 5),
  ('2019-04-14 02:25:00.000000', 'bronze', 'driver6', 'registration', 6),
  ('2019-04-14 02:26:00.000000', 'platinum', 'driver7', 'other', 7),
  ('2019-04-14 02:27:00.000000', 'bronze', 'driver8', 'other', 8),
  ('2019-04-14 02:29:00.000000', 'platinum', 'driver9', 'registration', 9);

INSERT INTO loyalty.statistics
  (home_zone, newbie, returnee)
VALUES
  ('moscow', 2, 1);
