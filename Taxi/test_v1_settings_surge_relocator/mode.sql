INSERT INTO config.modes
  (mode_id, mode_name, offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type)
VALUES
  (1488,'SuperSurge',True,100, 2000, 180000, ('ToPoint')::db.mode_type)
;
