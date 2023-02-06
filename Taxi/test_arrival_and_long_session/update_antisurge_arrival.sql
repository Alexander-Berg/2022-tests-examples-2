INSERT INTO checks.config (config_id, dry_run, info_push_count, warn_push_count, send_push) VALUES
  (44, FALSE, NULL, NULL, TRUE),
  (45, FALSE, NULL, NULL, TRUE);

INSERT INTO checks.antisurge_arrival
  (check_id, coef_surge, min_dest_surge, min_ride_time, config_id)
VALUES
  (1901, 0.9, 1.5, make_interval(secs=>2), 44),
  (1902, 1.8, 1.5, make_interval(secs=>2), 45);

INSERT INTO state.sessions(session_id, antisurge_arrival_id, dbid_uuid, start,
  reposition_source_point, reposition_dest_point, reposition_dest_radius, mode_id, tariff_class) VALUES
  (1531, 1901, ('dbid777','888'), '2018-11-26T08:00:00+0000', point(30,60), point(30,60), 12, 'home', 'econom'),
  (1532, 1902, ('dbid777','999'), '2018-11-26T08:00:00+0000', point(30,60), point(30,60), 12, 'home', 'econom');

INSERT INTO state.checks(session_id) VALUES (1531), (1532);
