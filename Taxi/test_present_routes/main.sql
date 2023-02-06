INSERT INTO config.points (
    position
)
VALUES (
    point(30.327056, 59.936243)
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
    route_id,
    name,
    is_deleted
)
VALUES (
    1,
    'main_route',
    FALSE
), (
    2,
    'deleted_route',
    TRUE
), (
    3,
    'route_without_points',
    FALSE
), (
    4,
    'some_route',
    FALSE
);

INSERT INTO config.route_points (
    route_id,
    point_id,
    point_order
)
VALUES (1, 1, 1),
       (2, 1, 1),
       (4, 1, 1)
;
