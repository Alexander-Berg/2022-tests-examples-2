INSERT INTO checks.config (config_id, dry_run, info_push_count, warn_push_count, send_push) VALUES
  (1,  FALSE, NULL, NULL, TRUE),
  (2,  FALSE, NULL, NULL, TRUE),
  (3,  FALSE, NULL, NULL, TRUE),
  (4,  FALSE, NULL, NULL, FALSE),
  (5,  FALSE, NULL, NULL, TRUE),
  (6,  FALSE, NULL, NULL, TRUE),
  (7,  FALSE, NULL, NULL, TRUE),
  (8,  FALSE, NULL, NULL, TRUE),
  (9,  FALSE, NULL, NULL, TRUE),
  (10, FALSE, NULL, NULL, FALSE),
  (11, FALSE, NULL, NULL, TRUE),
  (12, FALSE, NULL, NULL, TRUE),
  (13, FALSE, NULL, NULL, TRUE);

INSERT INTO checks.duration (check_id, span, due, left_time_deadline, left_time_coef, config_id) VALUES
  (1301, make_interval(mins => 15), NOW() + interval '1 hour', NULL,                      NULL, 1),
  (1302, make_interval(mins => 15), NOW() + interval '1 hour', NULL,                      NULL, 2),
  (1303, make_interval(mins => 15), NOW() + interval '1 hour', NULL,                      NULL, 3),
  (1304, make_interval(mins => 15), NOW() + interval '1 hour', NULL,                      NULL, 4),
  (1305, make_interval(mins => 15), NOW() + interval '1 hour', NULL,                      NULL, 5),
  (1306, make_interval(mins => 15), NOW() + interval '1 hour', make_interval(mins => 10), 0.1,  13);

INSERT INTO checks.arrival
  (check_id, eta, distance, config_id)
VALUES
  (1601, make_interval(secs=>5), 25, 6),
  (1602, make_interval(secs=>5), 25, 7),
  (1603, make_interval(secs=>5), 25, 8);

INSERT INTO checks.immobility (check_id, min_track_speed, position_threshold, max_immobility_time, config_id) VALUES
  (1701, 11, 22,  make_interval(secs=>33), 9),
  (1702, 11, 22,  make_interval(secs=>33), 10),
  (1703, 11, 22,  make_interval(secs=>33), 11);

INSERT INTO checks.surge_arrival
  (check_id, coef_surge, min_local_surge, min_ride_time, config_id)
VALUES
  (1801, 0.9, 0.5, make_interval(secs=>2), 12);

INSERT INTO state.sessions(session_id, duration_id, arrival_id, immobility_id, surge_arrival_id, dbid_uuid, start,
  reposition_source_point, reposition_dest_point, reposition_dest_radius, mode_id, tariff_class) VALUES
(1501, 1301, NULL, NULL, NULL, ('dbid777','888'), '2018-11-26T08:00:00+0000', point(30,60), point(30,60), 12, 'home', 'econom'),
(1502, 1302, 1601, 1701, NULL, ('1488','driverSS'), '2018-11-26T12:00:00+0000', point(30,60), point(30,60), 12, 'home', 'econom'),
(1503, 1303, NULL, NULL, NULL, ('1488','driverSS2'), '2018-11-26T08:00:00+0000', point(30,60), point(30,60), 12, 'home', 'econom'),
(1504, NULL, NULL, NULL, NULL, ('pg_park','pg_driver'), '2018-11-26T08:00:00+0000', point(30,60), point(30,60), 12, 'poi', 'econom'),
(1505, NULL, 1602, NULL, NULL, ('dbid','uuid'), '2018-11-26T12:00:00+0000', point(30,60), point(30,60), 12, 'poi', 'econom'),
(1506, NULL, 1603, NULL, NULL, ('dbid','uuid1'), '2018-11-26T08:00:00+0000', point(30,60), point(30,60), 12, 'poi', 'econom'),
(1507, 1306, NULL, NULL, NULL, ('dbid','uuid2'), '2018-11-26T11:45:00+0000', point(30,60), point(30,60), 12, 'surge', 'econom'),
(1508, NULL, NULL, NULL, 1801, ('dbid777','uuid'), '2018-11-26T08:00:00+0000', point(30,60), point(30,60), 12, 'surge', 'econom'),
(1509, 1304, NULL, 1702, NULL, ('dbid777','uuid1'), '2018-11-26T08:00:00+0000', point(30,60), point(30,60), 12, 'surge', 'econom'),
(1510, 1305, NULL, 1703, NULL, ('dbid777','uuid2'), '2018-11-26T08:00:00+0000', point(30,60), point(30,60), 12, 'surge', 'econom')
;

INSERT INTO state.immobility(immobility_violations)  SELECT(0) FROM generate_series(1,10);
INSERT INTO state.out_of_area (violations) SELECT(0) FROM generate_series(1,10);
INSERT INTO state.route(last_checks_count) SELECT(0) FROM generate_series(1,10);
INSERT INTO state.checks(session_id, immobility_state_id, route_state_id, out_of_area_state_id) SELECT i+1500, i, i, i FROM generate_series(1, 10) i;
