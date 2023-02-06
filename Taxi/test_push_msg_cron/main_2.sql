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
    (7, point(30.06, 60.06)),
    (8, point(30.07, 60.07)),
    (9, point(30.08, 60.08)),
    (10, point(30.09, 60.09)),
    (11, point(30.10, 60.10)),
    (12, point(30.11, 60.11)),
    (13, point(30.12, 60.12));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 2, 'stop1', NULL),
    (2, 3, 'stop2', 'stop__2'),
    (3, 5, 'stop3', 'stop__3'),
    (4, 7, 'stop4', NULL),
    (5, 9, 'stop5', NULL),
    (6, 11, 'stop6', NULL),
    (8, 12, 'stop8', NULL),
    (7, 13, 'stop7', NULL);

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
    route_id, name, is_cyclic
)
VALUES
    (1, 'route11', TRUE),
    (2, 'route22', FALSE),
    (3, 'route33', FALSE);

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
  (1, 8, 8),
  (1, 9, 9),
  (1, 10, 10),
  (1, 11, 11),
  (1, 12, 12),
  (1, 13, 13),
  (3, 10, 1),
  (3, 11, 2),
  (3, 12, 3),
  (3, 13, 4),
  (2, 1, 1),
  (2, 2, 2),
  (2, 3, 3),
  (2, 4, 4),
  (2, 5, 5);

INSERT INTO state.shuttles (
    driver_id, route_id, capacity, ticket_length
)
VALUES
    (('dbid1', 'uuid1')::db.driver_id, 1, 16, 3),
    (('dbid2', 'uuid2')::db.driver_id, 1, 16, 3),
    (('dbid3', 'uuid3')::db.driver_id, 2, 16, 3);

INSERT INTO state.matching_offers (
    offer_id,
    yandex_uid,
    shuttle_id,
    route_id,
    order_point_a,
    order_point_b,
    pickup_stop_id,
    pickup_lap,
    dropoff_stop_id,
    dropoff_lap,
    price,
    passengers_count,
    created_at,
    expires_at
)
VALUES
('2fef68c9-25d0-4174-9dd0-bdd1b3730775', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('427a330d-2506-464a-accf-346b31e288b9', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('5c76c35b-98df-481c-ac21-0555c5e51d21', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('5c76c53b-98aa-481c-ac21-0555c5e51d12', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000');

INSERT INTO state.passengers (
    yandex_uid,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    booking_id,
    offer_id,
    user_id,
    locale,
	status,
    dropoff_lap
)
VALUES (
           '0123456789',
           1,
           1,
           4,
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           'user_id_11',
           'ru',
		   'transporting',
            1
       ), (
           '9012345678',
           2,
           8,
           2,
           '427a330d-2506-464a-accf-346b31e288b9',
           '427a330d-2506-464a-accf-346b31e288b9',
           'user_id_22',
           'en',
		   'transporting',
           2
       ), (
           '8901234567',
           3,
           1,
           3,
           '5c76c35b-98df-481c-ac21-0555c5e51d21',
           '5c76c35b-98df-481c-ac21-0555c5e51d21',
           'user_id_33',
           'en',
		   'transporting',
           1
       );

INSERT INTO state.communications (
    booking_id,
    push_type,
    created_at
)
VALUES (
           '5c76c35b-98df-481c-ac21-0555c5e51d21',
           'shuttle.finishing',
           '2020-05-28T10:40:55');

INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    lap,
    begin_stop_id,
    next_stop_id,
    updated_at,
    advanced_at
)
VALUES
    (1, 1, 1, 4, NOW(), NOW()),
    (2, 2, 1, 2, NOW(), NOW()),
    (3, 1, 1, 1, NOW(), NOW());
