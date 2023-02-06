INSERT INTO config.usage_rules
  (mode_id,change_interval,day_usage_limit,week_usage_limit)
  VALUES
  (1, interval '7 day', 2, NULL),
  (2, NULL, 1, 5);

INSERT INTO config.display_rules (mode_id, image, tanker_key) VALUES
  (1, 'follow_track', 'home.restrictions.track'),
  (1, 'keep_moving', 'home.restrictions.move'),
  (2, 'follow_track', 'poi.restrictions.track'),
  (2, 'keep_moving', 'poi.restrictions.move');
