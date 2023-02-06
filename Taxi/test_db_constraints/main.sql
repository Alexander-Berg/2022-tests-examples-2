INSERT INTO config.points (
    point_id,
    position
)
VALUES (1, point(29.99, 59.99)),
       (2, point(30.00, 60.00)),
       (3, point(30.01, 60.01));

INSERT INTO config.stops (
    stop_id,
    point_id,
    name,
    ya_transport_stop_id
)
VALUES (1, 1, 'main_stop', 'stop__123'),
       (2, 3, 'stop_5', 'stop__5');

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
       (1, 2, 2),
       (1, 3, 3);

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    ticket_length,
    capacity,
    vfh_id
)
VALUES (
    1,
    ('dbid_0', 'uuid_0')::db.driver_id,
    1,
    3,
    16,
    '1234567890'
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
    (1, 1, 1, 1, NOW(), NOW());

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
VALUES (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '0123456789',
    1,
    1,
    point(30, 60),
    point(31, 61),
    1,
    1,
    1,
    1,
    '(10,RUB)',
    1,
    '2022-01-17T18:00:00+0000',
    '2023-01-24T18:18:00+0000'
);

