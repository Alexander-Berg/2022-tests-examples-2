INSERT INTO check_rules.duration
  (duration_id, due, _span)
VALUES
  (1, NULL, make_interval(secs=>3600)),
  (2, '2018-10-12T16:03:11', NULL),
  (3, '2018-10-12T16:05:00', make_interval(secs=>3600));

INSERT INTO check_rules.arrival
  (arrival_id, _eta, distance)
VALUES
  (1,  make_interval(secs=>30), 10);

INSERT INTO check_rules.immobility
  (immobility_id, min_track_speed, position_threshold, _max_immobility_time)
VALUES
  (1, 10, 100, make_interval(secs=>10));

INSERT INTO config.check_rules
  (mode_id, zone_id, duration_id, arrival_id, immobility_id)
VALUES
  (1, 1, 1, 1, 1);
