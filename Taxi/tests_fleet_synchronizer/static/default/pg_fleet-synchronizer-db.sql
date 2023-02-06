INSERT INTO auxiliary.cursors
  (app_family, task_type, last_updated_ts)
VALUES
  ('vezet', 'drivers_incremental', '0_1570000000_0'),
  ('vezet', 'parks_incremental', '0_1570000000_0')
ON CONFLICT DO NOTHING;
