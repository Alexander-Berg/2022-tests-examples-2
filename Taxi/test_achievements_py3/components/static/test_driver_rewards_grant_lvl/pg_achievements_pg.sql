INSERT INTO achievements_pg.rewards
  (code, category, has_locked_state, is_leveled, has_progress, levels)
VALUES
  ('express', '', TRUE, FALSE, FALSE, '{}'),
  ('star', '', TRUE, FALSE, FALSE, '{}'),
  ('bad_levels', '', TRUE, TRUE, FALSE, '{}'),
  ('driver_years', '', TRUE, TRUE, FALSE, '{1,2,3}'),
  ('5_stars', '', TRUE, TRUE, TRUE, '{100,300,500}')
;

INSERT INTO achievements_pg.driver_rewards
  (udid, reward_code, level, unlocked_at, seen_at)
VALUES
  ('udid1', 'express', 0, NULL, NULL),
  ('udid1', 'star', 1, '2019-02-01T01:00:00+03:00', NULL),
  ('udid2', 'driver_years', 1, '2019-02-01T01:00:00+03:00', NULL)
;
