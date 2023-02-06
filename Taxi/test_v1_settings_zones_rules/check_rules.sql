INSERT INTO check_rules.duration
  (_span, left_time_deadline, left_time_coef)
VALUES
  ('300 secs', '600 secs', 0.1),
  ('200 secs', '300 secs', 0.5),
  ('100 secs', NULL, NULL);

INSERT INTO check_rules.arrival
  (distance, _eta, air_distance)
VALUES
  (50, '30 secs', 10),
  (100, '60 secs', NULL),
  (150, '90 secs', 15);

INSERT INTO check_rules.immobility
  (min_track_speed, position_threshold, _max_immobility_time)
VALUES
  (12, 4, '90 secs'),
  (15, 6, '80 secs'),
  (18, 8, '70 secs');

INSERT INTO check_rules.antisurge_arrival
  (coef_surge, min_dest_surge, min_ride_time)
VALUES
  (0.9, 1.2, '50 secs'),
  (0.1, 1.8, '80 secs');

INSERT INTO check_rules.surge_arrival
  (time_coeff, surge_arrival_coef, min_arrival_surge, min_arrival_eta)
VALUES
  (0.9, 0.9, 1.1, '50 secs'),
  (0.1, 0.1, 1.0, '80 secs'),
  (-1.0, -1.0, -1.0, '0 secs');

INSERT INTO check_rules.surge_arrival_local
  (coef_surge, min_local_surge, min_ride_time)
VALUES
  (0.9, 1.1, '50 secs'),
  (0.1, 1.0, '80 secs'),
  (-1.0, -1.0, '0 secs');

INSERT INTO check_rules.out_of_area
  (first_warnings, last_warnings, min_distance_from_border, time_out_of_area)
VALUES
  (1, 3, 50, '40 secs'),
  (0, 10, 30, '90 secs'),
  (20, 100, 42, '0 secs');

INSERT INTO check_rules.route
  (check_interval, max_last_checks_count, max_violations_count, first_warnings, last_warnings, speed_dist_range, speed_dist_abs_range, speed_eta_range, speed_eta_abs_range, range_checks_compose_operator, speed_checks_compose_operator)
VALUES
  ('45 secs', 5, 3, 1, 2, ('-Infinity', -2)::db.double_range, (0, 2)::db.double_range, ('-Infinity', 10)::db.double_range, (0, 4)::db.double_range, 'AND', 'OR'),
  ('45 secs', 3, 2, 1, 2, ('-Infinity', -5)::db.double_range, (0, 5)::db.double_range, ('-Infinity', 30)::db.double_range, (0, 10)::db.double_range, 'OR', 'AND'),
  ('45 secs', 1, 1, 1, 2, ('-Infinity', 0)::db.double_range, (0, 1)::db.double_range, ('-Infinity', 3)::db.double_range, (0, 1)::db.double_range, 'OR', 'AND');

INSERT INTO check_rules.transporting_arrival(dry_run) VALUES (true), (false);
