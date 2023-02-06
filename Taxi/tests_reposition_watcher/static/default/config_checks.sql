INSERT INTO checks.config (config_id, dry_run, info_push_count, warn_push_count, send_push) VALUES
  (101, FALSE, NULL, NULL, TRUE),
  (102, FALSE, NULL, NULL, TRUE),
  (103, FALSE, NULL, NULL, TRUE),
  (104, FALSE, NULL, NULL, FALSE),
  (105, FALSE, NULL, NULL, TRUE),
  (106, FALSE, NULL, NULL, TRUE),
  (107, FALSE, NULL, NULL, TRUE),
  (108, FALSE, NULL, NULL, TRUE),
  (109, FALSE, NULL, NULL, TRUE),
  (110, FALSE, NULL, NULL, FALSE),
  (111, FALSE, NULL, NULL, TRUE),
  (112, FALSE, NULL, NULL, TRUE),
  (113, FALSE, NULL, NULL, TRUE);

INSERT INTO checks.conditions(
    condition_id,
    is_allowed_on_order) VALUES
    (101, true),
    (102, false);

INSERT INTO checks.duration (check_id, span, due, left_time_deadline, left_time_coef, config_id) VALUES
  (1301, make_interval(mins => 15), '2020-05-08 00:55:00', NULL,                      NULL, 101);

INSERT INTO checks.arrival
  (check_id, eta, distance, config_id)
VALUES
  (1601, make_interval(secs=>5), 25, 102),
  (1602, make_interval(secs=>5), 35, 103);

INSERT INTO checks.immobility (check_id, min_track_speed, position_threshold, max_immobility_time, config_id) VALUES
  (1701, 11, 22,  make_interval(secs=>33), 104),
  (1702, 21, 32,  make_interval(secs=>43), 105);

INSERT INTO checks.surge_arrival
  (check_id, coef_surge, min_local_surge, min_ride_time, config_id)
VALUES
  (1801, 0.9, 0.5, make_interval(secs=>2), 106);

INSERT INTO checks.out_of_area (check_id, min_distance_from_border, time_out_of_area, config_id, condition_id) VALUES
  (1901, 10, make_interval(mins => 15), 107, 101);

INSERT INTO checks.route (
        check_id,
        check_interval,
        max_last_checks_count,
        max_violations_count,
        speed_dist_range,
        speed_dist_abs_range,
        speed_eta_range,
        speed_eta_abs_range,
        range_checks_compose_operator,
        speed_checks_compose_operator,
        config_id,
        condition_id) VALUES
  (2001, '60 secs', 4, 3, ('-Infinity', 20)::checks.double_range, (1, 20)::checks.double_range, (-2, 5)::checks.double_range, (1, 5)::checks.double_range, 'AND', 'OR', 108, 102);

INSERT INTO checks.transporting_arrival (check_id, config_id) VALUES
(2101, 109);

INSERT INTO config.checks
  (zone_id, mode_id, submode_id, duration_id, arrival_id, immobility_id, surge_arrival_id, out_of_area_id, route_id, transporting_arrival_id)
VALUES
  (1,       2,       1,          1301,        1601,       1701,          1801,             1901,           2001,     2101),
  (1,       2,       NULL,       1301,        1601,       1702,          1801,             1901,           2001,     2101),
  (1,       1,       NULL,       NULL,        1602,       1702,          NULL,             1901,           2001,     NULL);
