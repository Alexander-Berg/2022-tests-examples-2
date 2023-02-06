INSERT INTO config.modes
  (mode_id, mode_name, offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type,                 work_modes)
VALUES
  (3,       'poi',     False,      1000,         2000,                 180000,               ('ToPoint')::db.mode_type, ARRAY['orders']);

