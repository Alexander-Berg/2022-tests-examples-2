INSERT INTO achievements_pg.rewards
  (code, is_leveled, levels)
VALUES
  ('star', FALSE, '{}'),
  ('express', FALSE, '{}'),
  ('top_fives', FALSE, '{}'),
  ('super_courier', FALSE, '{}'),
  ('covid_hero', FALSE, '{}'),
  ('bad_levels', TRUE, '{}'),
  ('driver_years', TRUE, '{1,2,3}')
;

INSERT INTO achievements_pg.uploads_schedule
  (id, reward_code, upload_type, period, yql, author, is_active)
VALUES
  ('sched_inactive', 'star', 'set_unlocked', 10, 'SELECT 1;', 'ivan', FALSE),
  ('sched_no_period', 'express', 'set_unlocked', NULL, 'SELECT 1;', 'ivan', TRUE),
  ('sched_bad_period', 'super_courier', 'set_unlocked', -1, 'SELECT 1;', 'ivan', TRUE),
  ('sched_no_yql', 'top_fives', 'set_unlocked', 10, NULL, 'ivan', TRUE),
  ('sched_set_covid_hero', 'covid_hero', 'set_unlocked', 10, 'SELECT 1;', 'ivan', TRUE),
  ('sched_bad_levels', 'bad_levels', 'set_unlocked', 10, 'SELECT 1,1;', 'ivan', TRUE),
  ('sched_leveled_ok', 'driver_years', 'set_unlocked', 10, 'SELECT 1,1;', 'ivan', TRUE)
;
