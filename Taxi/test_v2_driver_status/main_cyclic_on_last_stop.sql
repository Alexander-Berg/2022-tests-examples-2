INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.642933,55.735054)),
    (3, point(37.643129,55.734452)),
    (4, point(37.643037,55.734242)),
    (5, point(37.642790,55.734062)),
    (6, point(37.642023,55.734035)),
    (7, point(37.639896,55.737345)),
    (8, point(37.641867,55.737651));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 3, 'stop2', 'stop__2'),
    (3, 5, 'stop3', 'stop__3'),
    (4, 6, 'stop4', NULL),
    (5, 7, 'stop5', NULL),
    (6, 8, 'stop6', NULL);

INSERT INTO config.routes (
    route_id, name, is_cyclic
)
VALUES
    (1, 'route1', TRUE);

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
    (1, 8, 8);

INSERT INTO state.shuttles (
    shuttle_id, driver_id, route_id, capacity, ticket_length, work_mode
)
VALUES
    (1, ('dbid_0', 'uuid_1')::db.driver_id, 1, 16, 3, 'shuttle_fix');

INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    lap,
    begin_stop_id,
    next_stop_id,
    updated_at,
    advanced_at
)
VALUES
    (1, 1, 1, 3, NOW(), NOW())
;

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
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1),
    ('acfff773-398f-4913-b9e9-03bf5eda12ac', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1);

INSERT INTO state.passengers (
    booking_id,
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    shuttle_lap,
    status,
    offer_id,
    dropoff_lap
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', '012345678', 'userid_1', 1, 6, 3, 1, 'driving', 'acfff773-398f-4913-b9e9-03bf5eda22ac', 2),
    ('acfff773-398f-4913-b9e9-03bf5eda12ac', '012345679', 'userid_2', 1, 4, 1, 1, 'transporting', 'acfff773-398f-4913-b9e9-03bf5eda12ac', 2);

INSERT INTO state.booking_tickets (
    booking_id,
    status,
    code
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda12ac', 'confirmed', '123'),
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', 'issued', '234');
