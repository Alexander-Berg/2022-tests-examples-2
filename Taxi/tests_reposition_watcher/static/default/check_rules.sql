  INSERT INTO checks.duration
    (condition_id, config_id, due, span)
  VALUES
    (2, 3, '2010-04-04 06:00:00', '10:00:00'),
    (3, 4, '2011-04-04 06:00:00', '20:00:00'),
    (NULL, 5, '2012-04-04 06:00:00', '30:00:00'),
    (4, NULL, '2013-04-04 06:00:00', '40:00:00')
;

INSERT INTO checks.arrival
    (condition_id, eta, distance)
  VALUES
    (5, '10:00:00', 10),
    (6, '20:00:00', 20)
;

INSERT INTO checks.immobility
    (condition_id, min_track_speed, position_threshold, max_immobility_time)
  VALUES
    (NULL, 10, 20, '10:00:00'),
    (7, 15, 25, '20:00:00')
;

INSERT INTO checks.surge_arrival
    (condition_id, config_id, coef_surge, min_local_surge, min_ride_time)
  VALUES
    (NULL, 6, -1.5, 1.1, '00:00:10'),
    (8, 1, 0.5, 0.7, '00:00:20')
;

INSERT INTO checks.out_of_area
    (condition_id, min_distance_from_border, time_out_of_area)
  VALUES
    (NULL, 20, '00:00:10'),
    (9, 10, '00:00:20')
;

INSERT INTO checks.route
    (condition_id, config_id, check_interval, max_last_checks_count, max_violations_count,
    speed_dist_range, speed_dist_abs_range,
    speed_eta_range, speed_eta_abs_range, range_checks_compose_operator, speed_checks_compose_operator)
  VALUES
    (11, NULL, '00:00:10', 10, 12, (1.2,1.4), (1.2,1.4), (1.2,1.4), (1.2,1.4), 'OR', 'OR'),
    (10, 12, '00:00:10', 4, 16, (2.2,3.4), (1.2,1.4), (1.2,1.4), (1.2,1.4), 'AND', 'OR')
;
