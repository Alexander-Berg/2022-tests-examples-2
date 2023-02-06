INSERT INTO config.points (
    point_id,
    position
)
VALUES (
    2,
    point(31, 59)
), (
    3,
    point(32, 58)
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
), (
    3,
    3,
    'comp_stop'
);

INSERT INTO config.routes (
    route_id,
    name
)
VALUES (
    2,
    'aux_route'
);

INSERT INTO config.route_points (
    route_id,
    point_id,
    point_order
)
VALUES (
    2,
    2,
    1
), (
    2,
    3,
    2
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
