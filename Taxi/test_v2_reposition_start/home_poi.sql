INSERT INTO config.modes
  (mode_id, mode_name, offer_only, min_allowed_distance, max_allowed_distance, mode_type, work_modes)
VALUES
  (3,'poi',False, 2000, 180000, ('ToPoint')::db.mode_type, ARRAY['orders'])
;

INSERT INTO config.usage_rules
  (mode_id,change_interval,day_usage_limit,week_usage_limit)
VALUES
  (1, interval '7 day', 2, NULL),
  (3, NULL, 1, 5)
;
