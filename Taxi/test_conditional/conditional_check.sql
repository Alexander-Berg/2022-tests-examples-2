INSERT INTO state.sessions (
    session_id,
    dbid_uuid,
    START,
    reposition_source_point,
    reposition_dest_point,
    reposition_dest_radius,
    mode_id,
    tariff_class
) VALUES (
    1511,
    ('dbid777', '999'),
    '2018-11-26T06:00:00+0000',
    point(30, 60),
    point(30, 60),
    12,
    'home',
    'econom'
), (
    1512,
    ('dbid888', '777'),
    '2018-11-26T07:00:00+0000',
    point(30, 60),
    point(30, 60),
    12,
    'home',
    'econom'
);

INSERT INTO state.checks (
    session_id
) VALUES (
    1511
), (
    1512
);
