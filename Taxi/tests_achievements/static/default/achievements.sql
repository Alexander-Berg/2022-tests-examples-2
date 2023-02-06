-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

INSERT INTO achievements_pg.rewards
  (
    code,
    category,
    has_locked_state
  )
VALUES
  ('express', 'super_category', TRUE),
  ('star', 'other_category', FALSE),
  ('covid_hero', NULL, FALSE);

INSERT INTO achievements_pg.driver_rewards
  (udid, reward_code, level, updated_at, unlocked_at, seen_at)
VALUES
  -- unlocked but not seen yet (unlocked-new)
  ('udid1', 'express', 1, '2019-02-01T00:00:00+03:00', '2019-02-01T01:00:00+03:00', NULL ),
  ('udid1', 'covid_hero', 1, '2019-02-01T00:00:00+03:00', '2019-02-01T01:00:00+03:00', NULL ),
  -- still locked
  ('udid2', 'express', 1, '2019-02-01T00:00:00+03:00', '2019-02-01T01:00:00+03:00', NULL),
  -- unlocked and already seen
  ('udid2', 'star', 1, '2019-02-01T00:00:00+03:00', '2019-02-01T01:00:00+03:00', '2019-02-01T02:00:00+03:00');
