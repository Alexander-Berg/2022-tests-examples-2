INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.642933,55.735054)),
    (3, point(37.643129,55.734452)),
    (4, point(37.643148,55.734349)),
    (5, point(37.643055,55.734163)),
    (6, point(37.641628,55.733419)),
    (7, point(37.642938,55.735018)),
    (8, point(37.643055,55.734777)),
    (9, point(37.641965,55.733612)),
    (10, point(37.641406,55.733357)),
    (11, point(37.641161,55.733176));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 3, 'stop2', 'stop__2'),
    (3, 5, 'stop3', 'stop__3'),
    (4, 6, 'stop4', 'stop__4'),
    (5, 8, 'stop5', 'stop__5'),
    (6, 10, 'stop6', 'stop__6'),
    (7, 11, 'stop7', NULL);

INSERT INTO config.routes (
    route_id, name
)
VALUES
    (1, 'route1'),
    (2, 'route2');

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
  (2, 7, 1),
  (2, 8, 2),
  (2, 9, 3),
  (2, 10, 4),
  (2, 11, 5);

INSERT INTO state.shuttles (
    driver_id, route_id, capacity, ticket_length
)
VALUES
    (('dbid0', 'uuid0')::db.driver_id, 1, 16, 3),
    (('dbid1', 'uuid1')::db.driver_id, 2, 16, 3),
    (('dbid2', 'uuid2')::db.driver_id, 2, 16, 3);

INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    lap,
    begin_stop_id,
    next_stop_id,
    updated_at,
    advanced_at
)
VALUES
    (1, 1, 1, 2, NOW(), NOW()),
    (2, 0, 5, 5, NOW(), NOW()),
    (3, 0, 5, 5, NOW(), NOW());


UPDATE state.shuttle_trip_progress
SET block_reason = 'immobility'
WHERE shuttle_id = 3;
