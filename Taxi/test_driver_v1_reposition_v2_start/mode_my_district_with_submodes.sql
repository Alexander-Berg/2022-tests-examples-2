INSERT INTO config.modes
  (mode_id, mode_name,     offer_only, min_allowed_distance, max_allowed_distance, mode_type,                work_modes)
VALUES
  (19,      'my_district', False,      2000,                 1800000,              ('InArea')::db.mode_type, ARRAY['orders']);

INSERT INTO config.submodes
  (submode_id, submode_name, mode_id, is_default)
VALUES
  (101,        '30',         19,      true),
  (102,        '60',         19,      false),
  (103,        '90',         19,      false)
;

INSERT INTO config.usage_rules
  (mode_id, day_duration_limit_sum, week_duration_limit_sum)
VALUES
  (19,      '1 hours',              '6 hours')
;

INSERT INTO check_rules.duration
  (duration_id, _span)
VALUES
  (101,         '30 min'),
  (102,         '60 min'),
  (103,         '90 min')
;

INSERT INTO config.check_rules
  (zone_id, mode_id, submode_id, duration_id)
VALUES
  (1,       19,      NULL,       101),
  (1,       19,      101,        101),
  (1,       19,      102,        102),
  (1,       19,      103,        103)
;
