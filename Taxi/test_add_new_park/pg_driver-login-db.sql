INSERT INTO driver_login.table_by_ids
  (park_id, driver_profile_id, last_login_at, modified_at)
VALUES
  ('p1', 'd1', make_timestamp(2022, 01, 01, 12, 0, 0.0), make_timestamp(2022, 01, 01, 12, 0, 0.0)),
  ('p2', 'd2', make_timestamp(2022, 04, 04, 12, 0, 0.0), make_timestamp(2022, 04, 04, 12, 0, 0.0)),
  ('p3', 'd3', make_timestamp(2022, 03, 03, 12, 0, 0.0), make_timestamp(2022, 03, 03, 12, 0, 0.0));
