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
    driver_id, route_id, capacity, ticket_length
)
VALUES
    (('dbid0', 'uuid0')::db.driver_id, 1, 4, 3),
    (('dbid1', 'uuid1')::db.driver_id, 1, 5, 3),
    (('dbid2', 'uuid2')::db.driver_id, 2, 6, 3),
    (('dbid3', 'uuid3')::db.driver_id, 3, 6, 3)
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
    (1, 1, 1, 2, NOW(), NOW()),
    (2, 1, 2, 3, NOW(), NOW()),
    (3, 1, 1, 2, NOW(), NOW())
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
    ('2fef68c9-25d0-4174-9dd0-bdd1b3730775', '0123456784', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('427a330d-2506-464a-accf-346b31e288b2', '0123456785', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('693b28d3-6317-4106-acdd-2bb59e990e0d', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('427a330d-2506-454a-accf-346b31e288b4', '0123456781', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('427a330d-2506-464a-accf-346b31e288b5', '0123456782', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('427a330d-2506-464a-accf-346b31e288b6', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('427a330d-2506-464a-accf-346b31e288b7', '0123456781', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('427a330d-2506-464a-accf-346b31e288b8', '0123456782', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('427a330d-2506-464a-accf-346b31e288a7', '0123456783', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('427a330d-2506-464a-accf-346b31e288b9', '0123456783', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000');

INSERT INTO state.passengers (
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    booking_id,
    offer_id,
    status,
    origin,
    created_at,
    finished_at,
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
           'transporting',
           'application',
           '2020-09-14T15:15:16',
            null,
            1
       ), (
           '9012345678',
           'userid_2',
           1,
           1,
           3,
           '427a330d-2506-464a-accf-346b31e288b2',
           '427a330d-2506-464a-accf-346b31e288b2',
           'transporting',
           'application',
           '2020-09-14T15:15:16',
            null,
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
           'application',
           '2020-09-14T15:15:16',
            null,
           1
       ), (
           null,
           null,
           1,
           1,
           2,
           '427a330d-2506-454a-accf-346b31e288b4',
           '427a330d-2506-454a-accf-346b31e288b4',
           'cancelled',
           'street_hail',
           '2020-09-14T15:15:16',
           '2020-09-14T15:20:16',
           1
       ), (
           null,
           null,
           1,
           1,
           2,
           '427a330d-2506-464a-accf-346b31e288b5',
           '427a330d-2506-464a-accf-346b31e288b5',
           'finished',
           'street_hail',
           '2020-09-14T15:15:16',
           '2020-09-14T15:20:16',
           1
       ), (
           null,
           null,
           2,
           1,
           3,
           '427a330d-2506-464a-accf-346b31e288b6',
           '427a330d-2506-464a-accf-346b31e288b6',
           'created',
           'street_hail',
           '2020-09-14T15:15:16',
           null,
           1
       ), (
           '9712345678',
           'userid_7',
           2,
           2,
           3,
           '427a330d-2506-464a-accf-346b31e288b7',
           '427a330d-2506-464a-accf-346b31e288b7',
           'transporting',
           'application',
           '2020-09-14T15:15:16',
           null,
           1
       ), (
           '9812345678',
           'userid_8',
           3,
           1,
           3,
           '427a330d-2506-464a-accf-346b31e288b8',
           '427a330d-2506-464a-accf-346b31e288b8',
           'transporting',
           'application',
           '2020-09-14T15:15:16',
           null,
           1
       ), (
           null,
           null,
           3,
           1,
           3,
           '427a330d-2506-464a-accf-346b31e288a7',
           '427a330d-2506-464a-accf-346b31e288a7',
           'created',
           'street_hail',
           '2020-09-14T15:15:16',
           null,
           1
       ), (
           null,
           null,
           3,
           2,
           3,
           '427a330d-2506-464a-accf-346b31e288b9',
           '427a330d-2506-464a-accf-346b31e288b9',
           'finished',
           'street_hail',
           '2020-09-14T15:15:16',
           '2020-09-14T15:20:16',
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
           '427a330d-2506-464a-accf-346b31e288b2',
           'code2',
           'confirmed'
       ), (
           '693b28d3-6317-4106-acdd-2bb59e990e0d',
           'code3',
           'issued'
       ), (
           '427a330d-2506-454a-accf-346b31e288b4',
           'code4',
           'issued'
       ), (
           '427a330d-2506-464a-accf-346b31e288b5',
           'code5',
           'confirmed'
       ), (
           '427a330d-2506-464a-accf-346b31e288b6',
           'code6',
           'confirmed'
       ), (
           '427a330d-2506-464a-accf-346b31e288b7',
           'code7',
           'confirmed'
       ), (
           '427a330d-2506-464a-accf-346b31e288b8',
           'code8',
           'confirmed'
       ), (
           '427a330d-2506-464a-accf-346b31e288a7',
           'code9',
           'issued'
       ), (
           '427a330d-2506-464a-accf-346b31e288b9',
           'code9',
           'issued'
       );
