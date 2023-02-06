INSERT INTO config.modes
  (mode_id, mode_name, offer_only, min_allowed_distance, max_allowed_distance, mode_type)
VALUES
  (4, 'my_district', False, 2000, 1800000, ('InArea')::db.mode_type);
