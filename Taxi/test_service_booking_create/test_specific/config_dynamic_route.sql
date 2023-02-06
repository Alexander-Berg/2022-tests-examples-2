INSERT INTO config.points
    (point_id, position)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.643148,55.734349)),
    (3, point(37.642874,55.734083)),
    (4, point(37.642234,55.733778)),
    (5, point(37.640079,55.736952)),
    (6, point(37.641866, 55.737599)),
    (7, point(37.642345, 55.736403));

INSERT INTO config.stops
    (stop_id, point_id, name, ya_transport_stop_id, is_terminal)
VALUES
    (1, 1, 'stop1', NULL, TRUE),
    (2, 2, 'stop2', 'stop__2', FALSE),
    (3, 3, 'stop3', 'stop__3', FALSE),
    (4, 4, 'stop4', NULL, FALSE),
    (5, 5, 'stop5', NULL, FALSE),
    (6, 6, 'stop6', NULL, FALSE),
    (7, 7, 'stop7', NULL, FALSE);

INSERT INTO config.routes
    (route_id, name, is_dynamic)
VALUES
    (1, 'route', TRUE);

INSERT INTO config.route_points
    (route_id, point_id, point_order)
VALUES
    (1, 1, NULL),
    (1, 2, NULL),
    (1, 3, NULL),
    (1, 4, NULL),
    (1, 5, NULL),
    (1, 6, NULL),
    (1, 7, NULL);
