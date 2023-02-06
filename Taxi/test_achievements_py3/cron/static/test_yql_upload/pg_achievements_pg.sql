INSERT INTO achievements_pg.rewards
  (code, is_leveled, has_progress, levels)
VALUES
  ('star', FALSE, FALSE, '{}'),
  ('driver_years', TRUE, FALSE, '{1,2,3}'),
  ('5_stars', TRUE, TRUE, '{100,300,500}')
;
