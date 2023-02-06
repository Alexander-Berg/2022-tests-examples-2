INSERT INTO checks.route
  (route_id, check_interval, max_last_checks_count, max_violations_count, first_warnings, last_warnings, speed_dist_range, speed_dist_abs_range, speed_eta_range, speed_eta_abs_range, range_checks_compose_operator, speed_checks_compose_operator)
VALUES
  (101, '60 secs', 4, 3, 1, 1, ('-Infinity', 20)::db.double_range, (1, 20)::db.double_range, (-2, 5)::db.double_range, (1, 5)::db.double_range, 'AND', 'OR')
;

INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (1402, 1, IdId('888', 'dbid777'), '09-01-2018', 'dbid777_888_home', 'some home address', 'Postgresql', (3, 4), NULL);

INSERT INTO state.sessions
  (session_id, driver_id_id, active, point_id, start, "end", mode_id, destination_point, destination_radius)
VALUES
  (1502, IdId('888', 'dbid777'), TRUE, 1402, '2017-10-18T07:30:00+0000', NULL, 1, (3, 4), 12)
;


INSERT INTO state.checks
  (session_id, route_id, checking, last_check,                 route_check_data, route_last_check)
VALUES
  (1502,       101,            NULL,     '2017-10-18 07:37:05',    (0, 0, 0, 6527108.29290298, 939903.59417803, 6527108.29290298, 939903.59417803, '2017-10-18 07:37:05'), '2017-10-18 07:37:05')
;

