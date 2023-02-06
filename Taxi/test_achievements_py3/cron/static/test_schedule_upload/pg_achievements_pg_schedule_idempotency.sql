INSERT INTO achievements_pg.rewards
  (code)
VALUES
  ('star'),
  ('express'),
  ('top_fives')
;

INSERT INTO achievements_pg.uploads_schedule
  (id, reward_code, upload_type, period, yql, author, is_active)
VALUES
-- not started, because previous download was within idempotency offset
  ('sched_star', 'star', 'set_unlocked', 60, 'SELECT 1;', 'ivan', TRUE),
-- not started, because previous download was within schedule period
  ('sched_express', 'express', 'set_unlocked', 120, 'SELECT 1;', 'ivan', TRUE),
-- started OK
  ('sched_top_fives', 'top_fives', 'set_unlocked', 60, 'SELECT 1;', 'ivan', TRUE)
;

INSERT INTO achievements_pg.uploads
  (schedule_id, status, reward_code, upload_type, yql, author, created)
VALUES
  ('sched_star', 'new', 'star', 'set_unlocked', 'SELECT 1;', 'ivan', '2019-02-01T01:00:00+03:00'),
  ('sched_express', 'new', 'express', 'set_unlocked', 'SELECT 1;', 'ivan', '2019-02-01T00:00:00+03:00'),
  ('sched_top_fives', 'new', 'top_fives', 'set_unlocked', 'SELECT 1;', 'ivan', '2019-02-01T00:00:00+03:00')
;
