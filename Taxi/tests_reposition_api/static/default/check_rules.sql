INSERT INTO check_rules.duration
  (duration_id, due, _span)
VALUES
  (1, NULL, make_interval(secs=>3600)),
  (2, '2018-10-12T16:03:11', NULL),
  (3, '2018-10-12T16:05:00', make_interval(secs=>3600));

INSERT INTO config.check_rules
  (mode_id, zone_id, duration_id)
VALUES
  (1, 1, 1);
