INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.643148,55.734349)),
    (3, point(37.643055,55.734163)),
    (4, point(37.642163,55.733752)),
    (5, point(37.640079,55.736952)),
    (6, point(37.641867,55.737651)),
    (7, point(55.736403, 37.642345));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 3, 'stop2', 'stop__2'),
    (3, 4, 'stop3', 'stop__3'),
    (4, 5, 'stop4', NULL),
    (5, 6, 'stop5', NULL);

INSERT INTO config.routes (
    route_id, name, is_cyclic
)
VALUES
    (1, 'route1', TRUE),
    (2, 'route2', TRUE);

INSERT INTO config.route_points (
    route_id, point_id, point_order
)
VALUES
    (1, 1, 1),
    (1, 2, 2),
    (1, 3, 3),
    (1, 4, 4),
    (1, 5, 5),
    (1, 6, 6),
    (1, 7, 7),
    (2, 6, 1),
    (2, 7, 2);
