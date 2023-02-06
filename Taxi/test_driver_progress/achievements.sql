INSERT INTO achievements_pg.rewards
  (code, has_locked_state, is_leveled, has_progress, levels)
VALUES
  ('courier_orders', TRUE, TRUE, TRUE, '{300,1000,3000}')
;

INSERT INTO achievements_pg.driver_rewards
  (udid, reward_code, level, updated_at, unlocked_at, seen_at)
VALUES
  ('udid4', 'courier_orders', 300, '2019-02-01T00:00:00+03:00', '2019-02-01T00:00:00+03:00', NULL),
  ('udid4', 'courier_orders', 1000, '2019-02-01T00:00:00+03:00', '2019-02-01T00:00:00+03:00', NULL)
;

INSERT INTO achievements_pg.progresses
  (udid, reward_code, progress, updated_at)
VALUES
  ('udid4', 'courier_orders', 1000, '2019-02-01T00:00:00+03:00')
;
