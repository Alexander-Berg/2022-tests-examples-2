INSERT INTO check_rules.duration
  (duration_id, due,                   _span,                     left_time_deadline,         left_time_coef)
VALUES
  (11,          NULL,                  make_interval(secs=>3600), NULL,                       NULL),
  (12,          '2018-10-12T16:03:11', NULL,                      make_interval(secs => 600), 0.1),
  (13,          '2018-10-12T16:05:00', make_interval(secs=>3600), make_interval(secs => 600), NULL);

INSERT INTO check_rules.arrival
  (arrival_id, _eta,                    distance)
VALUES
  (21,         make_interval(secs=>30), 10);

INSERT INTO check_rules.immobility
  (immobility_id, min_track_speed, position_threshold, _max_immobility_time, dry_run)
VALUES
  (31,            10,              100,                make_interval(secs=>10), true);

INSERT INTO check_rules.surge_arrival
  (surge_arrival_id, time_coeff, surge_arrival_coef, min_arrival_surge, min_arrival_eta)
VALUES
  (41,               1.0,        1.1,                1.2,               make_interval(secs=>20));

INSERT INTO check_rules.out_of_area
  (out_of_area_id, first_warnings, last_warnings, min_distance_from_border, time_out_of_area)
VALUES
  (51,             2,              3,             20,                       make_interval(secs=>30));

INSERT INTO check_rules.route
  (route_id, check_interval, max_last_checks_count, max_violations_count, first_warnings, last_warnings,
  speed_dist_range, speed_dist_abs_range, speed_eta_range, speed_eta_abs_range,
  range_checks_compose_operator, speed_checks_compose_operator)
VALUES
  (61, make_interval(secs=>3600), 4, 5, 6, 7, (20,100)::db.double_range, (21, 100)::db.double_range,
  (22, 100)::db.double_range, (23, 100)::db.double_range, 'AND', 'OR');

INSERT INTO check_rules.conditions
  (condition_id, duration_id, out_of_area_id, is_allowed_on_order, is_allowed_on_busy)
VALUES
  (71,           12,          NULL,           TRUE,                TRUE),
  (72,           NULL,        51,             FALSE,               FALSE);
