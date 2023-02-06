INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(37.50, 55.75)),
    (2, point(37.51, 55.75)),
    (3, point(37.52, 55.75)),
    (11, point(37.50, 55.76)),
    (12, point(37.51, 55.76)),
    (13, point(37.52, 55.76))
;

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 2, 'stop2', 'stop__2'),
    (3, 3, 'stop3', 'stop__3'),
    (11, 11, 'stop11', NULL),
    (12, 12, 'stop12', 'stop__12'),
    (13, 13, 'stop13', 'stop__13')
;

INSERT INTO config.routes (
    route_id, name
)
VALUES
    (1, 'route1'),
    (2, 'route2'),
    (3, 'route3'),
    (4, 'route4')
;

INSERT INTO config.route_points (
  route_id, point_id, point_order
)
VALUES
  (1, 1, 1),
  (1, 2, 2),
  (1, 3, 3),
  (2, 11, 1),
  (2, 12, 2),
  (2, 13, 3),
  (3, 1, 1),
  (3, 11, 2)
;

INSERT INTO state.shuttles (
    driver_id, route_id, capacity, ticket_length, ended_at
)
VALUES
    (('dbid0', 'uuid0')::db.driver_id, 1, 4, 3, NULL),
    (('dbid1', 'uuid1')::db.driver_id, 1, 5, 3, '2020-09-14T14:15:10+0000'),
    (('dbid2', 'uuid2')::db.driver_id, 2, 6, 3, NULL),
    (('dbid3', 'uuid3')::db.driver_id, 3, 6, 3, NULL),
    (('dbid4', 'uuid4')::db.driver_id, 3, 6, 3, NULL)
;

INSERT INTO state.shuttle_trip_progress (
  shuttle_id,
  lap,
  begin_stop_id,
  next_stop_id,
  updated_at,
  average_speed,
  advanced_at
)
VALUES
    (1, 1, 1, 2, '2020-09-14T14:15:10+0000', 60, '2020-09-14T14:15:10+0000'), -- valid
    (2, 1, 2, 3, '2020-09-14T14:15:10+0000', 60, '2020-09-14T14:15:10+0000'), -- has ended_at
    (3, 1, 1, 2, '2020-09-14T14:15:10+0000', NULL, '2020-09-14T14:15:10+0000'), -- no average_speed
    (4, 1, 1, 2, '2020-09-14T10:15:10+0000', 40, '2020-09-14T10:15:10+0000'), -- too old position
    (5, 1, 1, 2, '2020-09-14T14:14:30+0000', 40, '2020-09-14T14:14:30+0000') -- valid
;
