INSERT INTO config.points (
    point_id,
    position
)
VALUES (
    2,
    point(31, 59)
);

INSERT INTO config.stops (
    stop_id,
    point_id,
    name
)
VALUES (
    2,
    2,
    'aux_stop'
);

INSERT INTO config.routes (
    route_id,
    name
)
VALUES (
    2,
    'aux_route'
);

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    capacity,
    ticket_length
)
VALUES (
    2,
    ('dbid_1', 'uuid_1')::db.driver_id,
    2,
    2,
    3
);

INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    lap,
    begin_stop_id,
    next_stop_id,
    updated_at,
    advanced_at
)
VALUES
    (2, 1, 1, 1, NOW(), NOW())
;

INSERT INTO state.passengers (
    yandex_uid,
    shuttle_id,
    stop_id,
    dropoff_lap
)
VALUES (
    '0123456789',
    2,
    1,
    1
);
