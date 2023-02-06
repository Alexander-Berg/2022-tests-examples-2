INSERT INTO checks.config
  (config_id, dry_run, info_push_count, warn_push_count, send_push)
VALUES
  (101,       FALSE,   3,               4,               TRUE),
  (102,       TRUE,    NULL,            NULL,            FALSE),
  (103,       FALSE,   NULL,            NULL,            TRUE),
  (104,       FALSE,   NULL,            NULL,            FALSE),
  (105,       FALSE,   NULL,            NULL,            TRUE),
  (106,       FALSE,   NULL,            NULL,            TRUE),
  (107,       FALSE,   NULL,            NULL,            TRUE),
  (108,       FALSE,   3,               4,               TRUE),
  (109,       TRUE,    6,               7,               TRUE),
  (110,       FALSE,   NULL,            NULL,            TRUE),
  (111,       FALSE,   NULL,            NULL,            FALSE),
  (112,       FALSE,   NULL,            NULL,            TRUE),
  (113,       FALSE,   NULL,            NULL,            TRUE),
  (114,       FALSE,   NULL,            NULL,            TRUE);

INSERT INTO checks.conditions
  (condition_id, is_allowed_on_order)
VALUES
  (101,          true),
  (102,          true),
  (103,          true),
  (104,          false),
  (105,          true),
  (106,          true),
  (107,          true),
  (108,          true),
  (109,          true);

INSERT INTO checks.duration
  (check_id, span,                      due,                   left_time_deadline, left_time_coef, config_id, condition_id)
VALUES
  (1301,     make_interval(mins => 15), '2020-05-08 00:55:00', NULL,               NULL,           101,       101),
  (1302,     make_interval(mins => 10), '2016-02-07 19:45:00', NULL,               NULL,           102,       102);

INSERT INTO checks.arrival
  (check_id, eta,                      distance, air_distance, config_id, condition_id)
VALUES
  (1601,     make_interval(secs=>300), 25,       10,           103,       103),
  (1602,     make_interval(secs=>300), 400,      500,          104,       104);

INSERT INTO checks.immobility
  (check_id, min_track_speed, position_threshold, max_immobility_time,      config_id, condition_id)
VALUES
  (1701,     11,              22,                 make_interval(secs=>33),  105,       105),
  (1702,     301,             401,                make_interval(secs=>501), 106,       106);

INSERT INTO checks.surge_arrival
  (check_id, coef_surge, min_local_surge, min_ride_time,          config_id)
VALUES
  (1801,     0.9,        0.5,             make_interval(secs=>2), 107);

INSERT INTO checks.out_of_area
  (check_id, min_distance_from_border, time_out_of_area,           config_id, condition_id)
VALUES
  (1901,     200,                      make_interval(secs => 150), 108,       108);

INSERT INTO checks.route
  (check_id, check_interval, max_last_checks_count, max_violations_count, speed_dist_range,                  speed_dist_abs_range,              speed_eta_range,                 speed_eta_abs_range,              range_checks_compose_operator, speed_checks_compose_operator, config_id, condition_id)
VALUES
  (2001,     '205 secs',     106,                   107,                  (11.2, 26.3)::checks.double_range, (31.5, 34.2)::checks.double_range, (2.5, 8.3)::checks.double_range, (1.8, 39.2)::checks.double_range, 'AND',                         'OR',                          109,       109);

INSERT INTO checks.transporting_arrival
  (check_id, config_id)
VALUES
  (2101,     109);

INSERT INTO config.checks
  (zone_id, mode_id, submode_id, duration_id, arrival_id, immobility_id, surge_arrival_id, out_of_area_id, route_id, transporting_arrival_id)
VALUES
  (1,       2,       1,          1301,        1601,       1701,          1801,             1901,           2001,     2101),
  (1,       2,       NULL,       1301,        1601,       1702,          1801,             1901,           2001,     2101),
  (1,       1,       NULL,       1302,        1602,       1702,          NULL,             1901,           2001,     NULL);
