INSERT INTO config.tags_zones_assignments
  (zone_id, mode_id, submode_id, session_tags,            completed_tags)
VALUES
  (1,       3,       NULL,       ARRAY['unexpected_tag'], NULL),
  (1,       3,       1,          ARRAY['unexpected_tag'], NULL),
  (2,       3,       NULL,       NULL,                    NULL),
  (2,       3,       1,          ARRAY['expected_tag'],   NULL)
;
