INSERT INTO checks.config(
    config_id,
    dry_run,
    info_push_count,
    warn_push_count,
    send_push
) VALUES (
    1,
    FALSE,
    NULL,
    NULL,
    TRUE
), (
    2,
    FALSE,
    NULL,
    NULL,
    FALSE
), (
    3,
    FALSE,
    NULL,
    NULL,
    TRUE
), (
    4,
    FALSE,
    NULL,
    NULL,
    TRUE
), (
    5,
    FALSE,
    NULL,
    NULL,
    TRUE
);

INSERT INTO checks.conditions(
    condition_id,
    is_allowed_on_order,
    is_allowed_on_busy
) VALUES (
    1,
    TRUE,
    TRUE
), (
    2,
    FALSE,
    FALSE
), (
    3,
    TRUE,
    FALSE
), (
    4,
    FALSE,
    TRUE
);

INSERT INTO checks.duration(
    check_id,
    span,
    due,
    left_time_deadline,
    left_time_coef,
    config_id,
    condition_id
) VALUES (
    1301,
    make_interval(mins => 15),
    NOW() + interval '1 hour',
    NULL,
    NULL,
    1,
    1
), (
    1302,
    make_interval(mins => 15),
    NOW() + interval '1 hour',
    NULL,
    NULL,
    2,
    2
), (
    1303,
    make_interval(mins => 15),
    NOW() + interval '1 hour',
    make_interval(mins => 10),
    0.1,
    3,
    NULL
);

INSERT INTO checks.arrival(
    check_id,
    eta,
    distance,
    config_id,
    condition_id
) VALUES (
    1601,
    make_interval(secs=>5),
    25,
    4,
    3
), (
    1602,
    make_interval(secs=>5),
    25,
    5,
    4
);

INSERT INTO state.sessions(
    session_id,
    duration_id,
    arrival_id,
    surge_arrival_id,
    dbid_uuid,
    "start",
    reposition_source_point,
    reposition_dest_point,
    reposition_dest_radius,
    mode_id,
    tariff_class
) VALUES (
    1501,
    NULL,
    1602,
    NULL,
    ('dbid','uuid'),
    '2018-11-26T12:00:00+0000',
    point(30,60),
    point(30,60),
    12,
    'poi',
    'econom'
), (
    1502,
    1302,
    NULL,
    NULL,
    ('dbid777','uuid1'),
    '2018-11-26T08:00:00+0000',
    point(30,60),
    point(30,60),
    12,
    'surge',
    'econom'
);

INSERT INTO state.checks(
    session_id
)
SELECT
    i + 1500
FROM
    generate_series(1, 2) AS i;
