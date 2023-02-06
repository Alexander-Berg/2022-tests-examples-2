INSERT INTO config.zones
  (zone_id, parent_zone, zone_name)
VALUES
  (2, 1, 'moscow');

INSERT INTO check_rules.duration
  (_span)
VALUES
  (make_interval(secs=>100));

INSERT INTO check_rules.arrival
  (distance, _eta)
VALUES
  (50, make_interval(secs=>30));

INSERT INTO check_rules.immobility
  (min_track_speed, position_threshold, _max_immobility_time)
VALUES
  (12, 4, make_interval(secs=>90)),
  (15, 6, make_interval(secs=>150));

INSERT INTO check_rules.antisurge_arrival
  (antisurge_arrival_id, coef_surge, min_dest_surge, min_ride_time)
VALUES
  (1, 1, 1.4, make_interval(secs => 50));

INSERT INTO check_rules.surge_arrival
  (time_coeff, surge_arrival_coef, min_arrival_surge, min_arrival_eta)
VALUES
  (0.9, 0.9, 1.1, make_interval(secs => 50));

INSERT INTO check_rules.transporting_arrival
  (dry_run)
VALUES
  (false);

INSERT INTO config.check_rules
  (zone_id, mode_id, duration_id, arrival_id, immobility_id, surge_arrival_id, transporting_arrival_id, antisurge_arrival_id, submode_id)
VALUES
  (1,       1,       1,           NULL,       1,             NULL,             NULL,                    NULL,              NULL),
  (1,       1,       NULL,        1,          NULL,          1,                1,                       1,                 1   ),
  (1,       1,       NULL,        NULL,       1,             NULL,             NULL,                    NULL,              2   ),
  (2,       1,       NULL,        1,          2,             1,                1,                       1,                 NULL);
