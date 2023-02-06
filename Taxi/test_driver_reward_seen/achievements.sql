-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

INSERT INTO achievements_pg.rewards
  (
    code,
    category,
    has_locked_state
  )
VALUES
  ('express', NULL, TRUE),
  ('star', NULL, TRUE),
  ('covid_hero', NULL, TRUE),
  ('top_fives', NULL, TRUE)
;

INSERT INTO achievements_pg.driver_rewards
  (udid, reward_code, level, seen_at, unlocked_at)
VALUES
  -- udid1:
  -- unlocked but not seen yet (unlocked-new)
  ('udid1', 'express', 1, NULL, '2019-02-01T01:00:00+03:00' ),
  ('udid1', 'star', 1, NULL, '2019-02-01T01:00:00+03:00' ),
  -- still locked, will not be marked seen
  ('udid1', 'covid_hero', 0, NULL, NULL ),
  -- unlocked and already seen
  ('udid1', 'top_fives', 1, '2019-02-01T01:00:00+03:00', '2019-02-01T01:00:00+03:00' ),

  -- udid2:
  -- unlocked but not seen yet (unlocked-new)
  ('udid2', 'express', 1, NULL , '2019-02-01T01:00:00+03:00'),
  ('udid2', 'top_fives', 1, NULL , '2019-02-01T01:00:00+03:00'),
  -- wrong level, will not be marked seen
  ('udid2', 'star', 2, NULL, '2019-02-01T01:00:00+03:00' ),
  -- still locked, will not be marked seen
  ('udid2', 'covid_hero', 0, NULL, NULL),

  ('udid3', 'express', 1, NULL, '2019-02-01T04:00:00+03:00' )
  ;
