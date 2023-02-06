INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(30.00, 60.00)),
    (2, point(30.01, 60.01)),
    (3, point(30.02, 60.02)),
    (4, point(30.03, 60.03)),
    (5, point(30.04, 60.04)),
    (6, point(30.05, 60.05));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 3, 'stop2', 'stop__2'),
    (3, 6, 'stop3', 'stop__3');

INSERT INTO config.routes (
    route_id, name
)
VALUES
    (1, 'route1');

INSERT INTO config.route_points (
  route_id, point_id, point_order
)
VALUES
  (1, 1, 1),
  (1, 2, 2),
  (1, 3, 3),
  (1, 4, 4),
  (1, 5, 5),
  (1, 6, 6);

INSERT INTO state.shuttles (
    driver_id, route_id, capacity, ticket_length
)
VALUES
    (('dbid0', 'uuid0')::db.driver_id, 1, 16, 3);

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
    created_at,
    expires_at
)
VALUES ( -- expired and used
           '5c76c35b-98df-481c-ac21-0555c5e51d21',
            '123456',
           1,
           1,
           point(30, 60),
           point(30, 60),
           1,
           1,
           2,
           1,
           '(0,RUB)',
           '2020-05-29T12:00:55+0000',
           '2020-05-29T12:40:55+0000'
       ),  ( -- expired and unused
           '427a330d-2506-464a-accf-346b31e288b9',
           '1234561',
           1,
           1,
           point(30, 60),
           point(30, 60),
           1,
           1,
           2,
           1,
           '(0,RUB)',
           '2020-05-29T12:00:55+0000',
           '2020-05-29T12:40:55+0000'
       ), ( -- not expired and unused
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           '1234562',
           1,
           1,
           point(30, 60),
           point(30, 60),
           2,
           1,
           3,
           1,
           '(0,RUB)',
           '2020-05-29T12:00:55+0000',
           '2020-05-29T13:40:55+0000'
       ), ( -- not expired and used
           '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
           '1234563',
           1,
           1,
           point(30, 60),
           point(30, 60),
           3,
           1,
           3,
           2,
           '(0,RUB)',
           '2020-05-29T12:00:55+0000',
           '2020-05-29T13:40:55+0000'
       );

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
           '5c76c35b-98df-481c-ac21-0555c5e51d21',
            1
       ), (
           '9012345678',
           'userid_2',
           1,
           1,
           2,
           '427a330d-2506-464a-accf-346b31e288b9',
           '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
           1
       );
