INSERT INTO achievements_pg.rewards
  (code, category, has_locked_state)
VALUES
  ('star', 'regular', TRUE),
  ('express', 'regular', TRUE),
  ('covid_hero', 'heroic', FALSE),
  ('1000_5star_rides', 'regular', TRUE);

  INSERT INTO achievements_pg.driver_rewards
    (udid, reward_code, level, unlocked_at, seen_at)
  VALUES
    ('udid1', 'express', 0, NULL, NULL),
    ('udid1', 'star', 1, '2019-02-01T01:00:00+03:00', NULL),

    ('udid2', 'covid_hero', 1, '2019-02-01T01:00:00+03:00', NULL),
    ('udid2', '1000_5star_rides', 1, '2019-02-01T01:00:00+03:00', NULL)
;
