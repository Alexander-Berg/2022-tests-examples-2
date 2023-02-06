INSERT INTO loyalty.loyalty_accounts
  (id, unique_driver_id, next_recount, last_active_at, status)
VALUES
  ('1', 'udid1', '2019-05-01 03:00:00.000000', NULL, 'newbie'),
  ('2', 'udid2', '2019-05-01 03:00:00.000000', NULL, 'newbie'),
  ('3', 'udid3', '2019-05-01 03:00:00.000000', '2020-01-01 00:00:00+03'::TIMESTAMPTZ, 'newbie'),
  ('4', 'udid4', '2019-05-01 03:00:00.000000', '2020-10-01 00:00:00+03'::TIMESTAMPTZ, 'newbie');
