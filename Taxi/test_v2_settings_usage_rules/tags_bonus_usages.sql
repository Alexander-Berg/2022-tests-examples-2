INSERT INTO config.modes
  (mode_id, mode_name, offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type)
VALUES
  (3,'poi',True,100, 2000, 180000, ('ToPoint')::db.mode_type);

INSERT INTO config.tags_bonus_usages
  (tag_id, tag_name, mode_id, day_bonus_usages, week_bonus_usages, day_bonus_duration_limit, week_bonus_duration_limit)
VALUES
  (NULL, 'selfemployed',      1,       3,                NULL,              NULL,                     NULL),
  (NULL, 'great_driver',      1,       NULL,             NULL,              '1 hour',                 '3 hours'),
  (NULL, 'great_driver',      3,       NULL,             5,                 '1 hour',                 '3 hours')
;
