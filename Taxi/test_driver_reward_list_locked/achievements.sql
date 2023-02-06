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
  ('covid_hero', NULL, FALSE),
  ('top_fives', NULL, TRUE)
;

INSERT INTO achievements_pg.driver_rewards
  (udid, reward_code, level, unlocked_at)
VALUES
  ('udid1', 'express', 1, NOW()),
  ('udid1', 'covid_hero', 1, NOW()),
  ('udid1', 'top_fives', 0, NULL)
  ;
