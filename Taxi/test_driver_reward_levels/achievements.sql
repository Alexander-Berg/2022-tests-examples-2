INSERT INTO achievements_pg.rewards
  (
    code,
    has_locked_state,
    is_leveled,
    has_progress,
    levels
  )
VALUES
  ('express', TRUE, FALSE, FALSE, '{}'),
  ('driver_years', TRUE, TRUE, FALSE, '{1,2}'),
  ('courier_orders', FALSE, TRUE, TRUE, '{300,1000,3000}')
;

INSERT INTO achievements_pg.driver_rewards
  (udid, reward_code, level, updated_at, unlocked_at, seen_at)
VALUES

  ('udid1', 'driver_years', 1, '2019-02-01T00:00:00+03:00', '2019-02-01T00:00:00+03:00', NULL ),

  ('udid2', 'express', 1, '2019-02-01T00:00:00+03:00', '2019-02-01T00:00:00+03:00', NULL ),
  ('udid2', 'driver_years', 1, '2019-02-01T00:00:00+03:00', '2019-02-01T00:00:00+03:00', '2019-02-01T02:00:00+03:00' ),

  ('udid3', 'driver_years', 1, '2019-02-01T00:00:00+03:00', '2019-02-01T00:00:00+03:00', '2019-02-01T02:00:00+03:00' ),
  ('udid3', 'driver_years', 2, '2019-02-01T00:00:00+03:00', '2019-02-01T00:00:00+03:00', NULL ),

  ('udid4', 'courier_orders', 0, '2019-02-01T00:00:00+03:00', NULL, NULL ), -- invalid level
  ('udid4', 'courier_orders', 300, '2019-02-01T00:00:00+03:00', '2019-02-01T00:00:00+03:00', NULL ),
  ('udid4', 'courier_orders', 500, '2019-02-01T00:00:00+03:00', '2019-02-01T00:00:00+03:00', NULL ), -- invalid level
  ('udid4', 'courier_orders', 1000, '2019-02-01T00:00:00+03:00', '2019-02-01T00:00:00+03:00', NULL )
;
