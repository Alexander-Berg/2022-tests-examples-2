INSERT INTO config.modes
  (mode_id, mode_name, offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type,                 work_modes)
VALUES
  (3,       'poi',     FALSE,      NULL,         2000,                 180000,               ('ToPoint')::db.mode_type, ARRAY['orders']);

INSERT INTO check_rules.duration
  (duration_id, due,  _span)
VALUES
  (1,           NULL, make_interval(secs=>3600));

INSERT INTO config.check_rules
  (mode_id, zone_id, duration_id, arrival_id, immobility_id)
VALUES
  (1,       1,       1,           NULL,       NULL);
