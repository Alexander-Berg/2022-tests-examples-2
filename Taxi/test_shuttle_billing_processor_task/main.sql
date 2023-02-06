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
    (3, 3, 'stop3', 'stop__3')
;

INSERT INTO config.routes (
    route_id, name
)
VALUES
    (1, 'route1')
;

INSERT INTO config.route_points (
  route_id, point_id, point_order
)
VALUES
  (1, 1, 1),
  (1, 2, 2),
  (1, 3, 3)
;

INSERT INTO state.shuttles (
    driver_id, route_id, capacity, ticket_length
)
VALUES
    (('dbid0', 'uuid0')::db.driver_id, 1, 4, 3)
;

INSERT INTO state.shuttle_trip_progress (
  shuttle_id,
  lap,
  begin_stop_id,
  next_stop_id,
  updated_at,
  advanced_at
)
VALUES
    (1, 1, 1, 2, NOW(), NOW())
;

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
('693b28d3-6317-4106-acdd-2bb59e990e0d', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000');

INSERT INTO state.passengers (
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    booking_id,
    offer_id,
    status,
    created_at,
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
           'finished',
           '2020-09-14T09:15:16+0000',
            1
       ), (
           '9912345678',
           'userid_9',
           1,
           2,
           3,
           '427a330d-2506-464a-accf-346b31e288b9',
           '427a330d-2506-464a-accf-346b31e288b9',
           'finished',
           '2020-09-14T09:15:16+0000',
            1
       ), (
            '9112345678',
            'userid_3',
            1,
            2,
            3,
            '693b28d3-6317-4106-acdd-2bb59e990e0d',
            '693b28d3-6317-4106-acdd-2bb59e990e0d',
            'driving',
            '2020-09-14T09:15:17+0000',
           1
       );

INSERT INTO state.booking_tickets (
    booking_id,
    code,
    status
)
VALUES (
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           'code1',
           'confirmed'
       ), (
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           'code2',
           'confirmed'
       ), (
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           'code3',
           'issued'
       ), (
           '427a330d-2506-464a-accf-346b31e288b9',
           'code4',
           'confirmed'
       ), (
           '427a330d-2506-464a-accf-346b31e288b9',
           'code5',
           'revoked'
       ), (
           '693b28d3-6317-4106-acdd-2bb59e990e0d',
           'code6',
           'confirmed'
       );

INSERT INTO state.order_billing_requests (
    booking_id,
    "timezone",
    nearest_zone,
    state
) VALUES
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    'Europe/Moscow',
    'moscow',
    'requested'
), (
    '427a330d-2506-464a-accf-346b31e288b9',
    'Europe/Moscow',
    'moscow',
    'requested'
);
