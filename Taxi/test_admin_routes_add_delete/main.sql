INSERT INTO config.points (
    position
)
VALUES (
    point(30, 60)
);

INSERT INTO config.stops (
    point_id,
    name
)
VALUES (
    1,
    'main_stop'
);

INSERT INTO config.routes (
    name
)
VALUES (
    'main_route'
);

INSERT INTO state.shuttles (
    driver_id,
    route_id,
    capacity,
    ticket_length
)
VALUES (
    ('dbid_0', 'uuid_0')::db.driver_id,
    1,
    16,
    3
);
