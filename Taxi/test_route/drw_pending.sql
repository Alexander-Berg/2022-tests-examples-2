INSERT INTO checks.conditions(
    condition_id,
    is_allowed_on_order
) VALUES (
    101,
    TRUE
), (
    102,
    TRUE
),(
    103,
    TRUE
);

INSERT INTO checks.config (
    config_id,
    dry_run,
    info_push_count,
    warn_push_count,
    send_push
) VALUES (
    101,
    FALSE,
    1,
    1,
    TRUE
), (
    102,
    FALSE,
    1,
    1,
    TRUE
), (
    103,
    FALSE,
    1,
    1,
    TRUE
);

INSERT INTO checks.route (
    check_id,
    condition_id,
    config_id,
    check_interval,
    max_last_checks_count,
    max_violations_count,
    speed_dist_range,
    speed_dist_abs_range,
    speed_eta_range,
    speed_eta_abs_range,
    range_checks_compose_operator,
    speed_checks_compose_operator
) VALUES (
    101,
    101,
    101,
    '60 secs',
    4,
    3,
    ('-Infinity', 20)::checks.double_range,
    (1, 20)::checks.double_range,
    (-2, 5)::checks.double_range,
    (1, 5)::checks.double_range,
    'AND',
    'OR'
), (
    102,
    102,
    102,
    '60 secs',
    4,
    3,
    ('-Infinity', 20)::checks.double_range,
    (1, 20)::checks.double_range,
    (-2, 5)::checks.double_range,
    (1, 5)::checks.double_range,
    'AND',
    'OR'
),(
    103,
    103,
    103,
    '60 secs',
    4,
    3,
    ('-Infinity', 20)::checks.double_range,
    (1, 20)::checks.double_range,
    (-2, 5)::checks.double_range,
    (1, 5)::checks.double_range,
    'AND',
    'OR'
);

INSERT INTO state.route(
    state_id,
    last_check,
    start_time,
    violations_count,
    failed_checks_count,
    last_checks_count,
    drw,
    drw_dry_run
) VALUES (
     101,
     '2020-06-25T12:59:00+0000',
     '2020-06-25T12:00:00+0000',
     0,
     0,
     0,
     TRUE,
     FALSE
), (
    102,
    '2020-06-25T12:59:00+0000',
    '2020-06-25T12:00:00+0000',
    0,
    0,
    0,
    TRUE,
    FALSE
), (
    103,
    '2020-06-25T12:59:00+0000',
    '2020-06-25T12:00:00+0000',
    0,
    0,
    0,
    TRUE,
    FALSE
);

INSERT INTO state.sessions (
    session_id,
    route_id,
    dbid_uuid,
    START,
    reposition_source_point,
    reposition_dest_point,
    reposition_dest_radius,
    mode_id,
    tariff_class,
    drw_state
) VALUES (
    1511,
    101,
    ('dbid777', '999'),
    '2020-06-25T12:00:00+0000',
    point(30, 60),
    point(30, 60),
    12,
    'home',
    'econom',
    'Pending'
), (
    1512,
    102,
    ('dbid888', '777'),
    '2020-06-25T12:00:00+0000',
    point(30, 60),
    point(30, 60),
    12,
    'home',
    'econom',
    'Active'
),  (
    1513,
    103,
    ('dbid333', '333'),
    '2020-06-25T12:00:00+0000',
    point(30, 60),
    point(30, 60),
    12,
    'home',
    'econom',
    'Pending'
);

INSERT INTO state.checks (
    session_id,
    route_state_id
) VALUES (
    1511,
    101
), (
    1512,
    102
), (
    1513,
    103
);
