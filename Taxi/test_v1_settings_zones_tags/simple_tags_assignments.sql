INSERT INTO config.tags_zones_assignments
  (zone_id, mode_id, submode_id, session_tags, completed_tags)
VALUES
  (1, 1, NULL, ARRAY['tag_1'], ARRAY['tag_2']),
  (1, 1, 1, ARRAY['tag_3'], ARRAY['tag_4']),
  (1, 1, 2, ARRAY['tag_5'], NULL)
;
