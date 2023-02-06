INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(30.00, 60.00)),
    (2, point(30.01, 60.01)),
    (3, point(30.02, 60.02)),
    (4, point(30.03, 60.03)),
    (5, point(30.04, 60.04)),
    (6, point(30.05, 60.05)),
    (7, point(30.08, 60.08));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 3, 'stop2', 'stop__2'),
    (3, 5, 'stop3', 'stop__3'),
    (4, 6, 'stop4', NULL),
    (5, 7, 'stop5', 'stop__5');

INSERT INTO config.schedules (schedule)
VALUES ('{
  "timezone":"UTC",
  "intervals": [{
    "exclude": false,
    "day": [4]
  }, {
    "exclude": false,
    "daytime": [{
        "from": "11:00:00",
        "to": "18:00:00"
      }
    ]
  }],
  "repeat":{
    "interval": 1800,
    "origin": "start"
  }}'::jsonb);

INSERT INTO config.routes (
    route_id, name, is_deleted
)
VALUES
    (1, 'route1', FALSE),
    (2, 'route2', FALSE),
    (3, 'route3', FALSE),
    (4, 'route4', TRUE);

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
  (2, 1, 6),
  (2, 2, 5),
  (2, 3, 4),
  (2, 4, 3),
  (2, 5, 2),
  (2, 6, 1),
  (3, 1, 1),
  (3, 2, 2),
  (3, 3, 3),
  (4, 1, 1),
  (4, 2, 2),
  (4, 7, 3);

INSERT INTO state.shuttles (
    driver_id, route_id, capacity, ticket_length
)
VALUES
    (('dbid0', 'uuid0')::db.driver_id, 1, 16, 3),
    (('dbid1', 'uuid1')::db.driver_id, 2, 16, 3),
    (('dbid2', 'uuid2')::db.driver_id, 1, 16, 3);

INSERT INTO state.matching_offers(
    offer_id,
    shuttle_id,
    order_point_a,
    order_point_b,
    pickup_stop_id,
    pickup_lap,
    dropoff_stop_id,
    dropoff_lap,
    price,
    expires_at,
    created_at,
    route_id
)
VALUES
('2fef68c9-25d0-4174-9dd0-bdd1b3730775', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1),
('427a330d-2506-464a-accf-346b31e288b9', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1),
('5c76c35b-98df-481c-ac21-0555c5e51d21', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1);

INSERT INTO state.passengers (
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    booking_id,
    offer_id,
    dropoff_lap
)
VALUES (
           '0123456789',
           'userid_1',
           1,
           1,
           2,
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            1
       ), (
           '9012345678',
           'userid_2',
           1,
           1,
           2,
           '427a330d-2506-464a-accf-346b31e288b9',
           '427a330d-2506-464a-accf-346b31e288b9',
            1
       ), (
           '8901234567',
           'userid_3',
           2,
           2,
           3,
           '5c76c35b-98df-481c-ac21-0555c5e51d21',
           '5c76c35b-98df-481c-ac21-0555c5e51d21',
           1
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
    (1, 0, 1, 1, NOW(), NOW()),
    (2, 1, 4, 3, NOW(), NOW()),
    (3, 0, 1, 1, NOW(), NOW());
