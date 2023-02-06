INSERT INTO config.points (
    point_id,
    position
)
VALUES (1, point(30, 60)),
       (5, point(30, 60));

INSERT INTO config.stops (
    stop_id,
    point_id,
    name,
    ya_transport_stop_id
)
VALUES (1, 1, 'main_stop', 'stop__123'),
       (5, 5, 'stop_5', 'stop__5');

INSERT INTO config.routes (
    route_id,
    name
)
VALUES (
    1,
    'main_route'
);

INSERT INTO config.route_points (
    route_id,
    point_id,
    point_order
)
VALUES (1, 1, 1),
       (1, 5, 2);

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    capacity,
    ticket_length
)
VALUES
(
    1,
    ('dbid_0', 'uuid_0')::db.driver_id,
    1,
    16,
    3
),
(
    2,
    ('dbid_0', 'uuid_1')::db.driver_id,
    1,
    16,
    3
);

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
('2fef68c9-25d0-4174-9dd0-bdd1b3730776', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1);

INSERT INTO state.passengers (
    booking_id,
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    locale,
    created_at,
    status,
    offer_id,
    dropoff_lap
)
VALUES
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '0123456789',
    'user_id_1',
    1,
    1,
    5,
    'ru',
    '2020-05-18T15:00:00',
    'finished',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    1
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    '0123456789',
    'user_id_1',
    2,
    1,
    5,
    'ru',
    '2020-05-18T16:00:00',
    'driving',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    1
)
;
