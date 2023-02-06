INSERT INTO config.modes
  (mode_id, mode_name, offer_only, min_allowed_distance, max_allowed_distance, mode_type,                 client_attributes,          experimental, tags_prohibited,          work_modes)
VALUES
  (1,       'home',    False,      2000,                 180000,               ('ToPoint')::db.mode_type, '{"dead10cc": "deadbeef"}', True,         ARRAY['home_prohibited'], ARRAY['orders'])
;
