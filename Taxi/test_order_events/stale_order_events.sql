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
    '2018-11-26T07:59:00+0000',
    point(30, 60),
    point(30, 60),
    12,
    'home',
    'econom'
), (
    1513,
    ('dbid666', '888'),
    '2018-11-26T07:59:00+0000',
    point(30, 60),
    point(30, 60),
    12,
    'home',
    'econom'
), (
    1514,
    ('dbid111', '333'),
    '2018-11-26T07:59:00+0000',
    point(30, 60),
    point(30, 60),
    12,
    'home',
    'econom'
);

INSERT INTO state.order_events(
    session_id,
    event,
    occurred_at,
    ta_event
) VALUES (
    1511,
    'IN_PROGRESS',
    '2018-11-25T08:00:00+0000',
    NULL
), (
    1513,
    'IN_PROGRESS',
    '2018-11-26T07:00:00+0000',
    NULL
);
