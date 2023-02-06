INSERT INTO checks.config (
    config_id,
    dry_run
) VALUES (
    101,
    FALSE
), (
    102,
    FALSE
);

INSERT INTO checks.transporting_arrival (
    check_id,
    config_id
) VALUES (
    101,
    101
), (
    102,
    102
);

INSERT INTO state.transporting_arrival (
    state_id,
    order_in_progress
) VALUES (
    101,
    TRUE
), (
    102,
    FALSE
);

INSERT INTO state.sessions (
    session_id,
    transporting_arrival_id,
    dbid_uuid,
    START,
    reposition_source_point,
    reposition_dest_point,
    reposition_dest_radius,
    mode_id,
    tariff_class
) VALUES (
    1511,
    101,
    ('dbid777', '999'),
    '2018-11-26T07:59:00+0000',
    point(30, 60),
    point(30, 60),
    12,
    'home',
    'econom'
), (
    1512,
    102,
    ('dbid888', '777'),
    '2018-11-26T07:59:00+0000',
    point(30, 60),
    point(30, 60),
    12,
    'home',
    'econom'
);

INSERT INTO state.checks (
    session_id,
    transporting_arrival_state_id
) VALUES (
    1511,
    101
), (
    1512,
    102
);
