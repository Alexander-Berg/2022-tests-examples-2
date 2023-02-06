INSERT INTO checks.conditions(
    is_allowed_on_order
) VALUES (
    TRUE
), (
    TRUE
);

INSERT INTO checks.config(
    config_id, dry_run, info_push_count, warn_push_count, send_push
) VALUES (
    1,         TRUE,    NULL,            NULL,            TRUE
), (
    2,         FALSE,   NULL,            NULL,            TRUE
);

INSERT INTO checks.duration(
    condition_id, config_id, due,                   span
) VALUES (
    1,            1,         '2010-01-01 01:00:00', '1:00:00'
), (
    2,            2,         '2010-01-01 01:00:00', '1:00:00'
  );

INSERT INTO state.sessions(
    session_id,
    dbid_uuid,
    start,
    reposition_source_point,
    reposition_dest_point,
    reposition_dest_radius,
    mode_id,
    duration_id,
    arrival_id,
    immobility_id,
    surge_arrival_id,
    out_of_area_id,
    route_id,
    tariff_class
) VALUES (
    1,
    ('dbid777','999'),
    '2010-01-01 00:00:00',
    '(1,2)',
    '(3,4)',
    12,
    'home',
    1,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'econom'
), (
    2,
    ('dbid888','777'),
    '2010-01-01 00:00:00',
    '(1,2)',
    '(3,4)',
    12,
    'home',
    2,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'econom'
);

INSERT INTO state.checks(
    session_id
) VALUES (
    1
), (
    2
);
