INSERT INTO config.points (
    point_id,
    position
)
VALUES (1, point(29.99, 59.99)),
       (2, point(30, 60)),
       (5, point(30, 60));

INSERT INTO config.stops (
    stop_id,
    point_id,
    name,
    ya_transport_stop_id
)
VALUES (1, 2, 'main_stop', 'stop__123'),
       (5, 5, 'stop_5', 'stop__5');

INSERT INTO config.routes (
    route_id,
    name
)
VALUES (
    1,
    'main_route'
), (
    2,
    'alternative_route'
);

INSERT INTO config.route_points (
    route_id,
    point_id,
    point_order
)
VALUES (1, 1, 1),
       (1, 2, 2),
       (1, 5, 3),
       (2, 1, 1),
       (2, 2, 2),
       (2, 5, 3);

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    ticket_length,
    capacity
)
VALUES (
    1,
    ('dbid_0', 'uuid_0')::db.driver_id,
    1,
    3,
    15
), (
    2,
    ('dbid_2', 'uuid_2')::db.driver_id,
    2,
    4,
    16
), (
    3,
    ('dbid_3', 'uuid_3')::db.driver_id,
    1,
    3,
    16
), (
    4,
    ('dbid_4', 'uuid_4')::db.driver_id,
    1,
    2,
    16
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
    (1, 1, 1, 1, NOW(), NOW()),
    (2, 1, 1, 1, NOW(), NOW()),
    (3, 1, 1, 1, NOW(), NOW()),
    (4, 1, 1, 1, NOW(), NOW());

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
    expires_at,
    external_passenger_id
)
VALUES
('2fef68c9-25d0-4174-9dd0-bdd1b3730775', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', 'external_pax'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730779', 'legacy_client', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', NULL),
('2fef68c9-25d0-4174-9dd0-bdd1b3730777', '1234564', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:17:00+0000', NULL),
('5c76c35b-98df-481c-ac21-0555c5e51d21', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', NULL),
('5c76c35b-98df-481c-ac21-0555c5e51d22', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 3, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', NULL),
('5c76c35b-98df-481c-ac21-0555c5e51d23', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 16, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', NULL),
('2fef68c9-25d0-4174-9dd0-bdd1b3730666', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(0,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', NULL);
