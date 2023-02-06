INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.643148,55.734349)),
    (3, point(37.643055,55.734163)),
    (4, point(37.642163,55.733752)),
    (5, point(37.640079,55.736952)),
    (6, point(37.641867,55.737651)),
    (7, point(55.736403, 37.642345));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 3, 'stop2', 'stop__2'),
    (3, 4, 'stop3', 'stop__3'),
    (4, 5, 'stop4', NULL),
    (5, 6, 'stop5', NULL);

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
  (1, 7, 7);

INSERT INTO state.shuttles (
    driver_id, route_id, is_fake, capacity, ticket_length
)
VALUES
    (('dbid0', 'uuid0')::db.driver_id, 1, FALSE, 4, 3),
    (('dbid1', 'uuid1')::db.driver_id, 1, FALSE, 4, 3),
    (('dbid2', 'uuid2')::db.driver_id, 1, FALSE, 4, 3),
    (('dbid3', 'uuid3')::db.driver_id, 1, FALSE, 4, 3);

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
VALUES
('acfff773-398f-4913-b9e9-03bf5eda22ac', '012345678', 1, 1, point(30, 60), point(31, 61), 5, 4, 2, 5, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('acfff773-398f-4913-b9e9-03bf5eda26ac', '012345673', 2, 1, point(30, 60), point(31, 61), 5, 2, 2, 3, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('acfff773-398f-4913-b9e9-03bf5eda25ac', '012345670', 3, 1, point(30, 60), point(31, 61), 5, 6, 2, 7, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('acfff773-398f-4913-b9e9-03bf5eda24ac', '012345671', 4, 1, point(30, 60), point(31, 61), 5, 1, 2, 2, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('acfff773-398f-4913-b9e9-03bf5eda23ac', '012345672', 1, 1, point(30, 60), point(31, 61), 5, 1, 2, 2, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730775', '0123456789', 1, 1, point(30, 60), point(31, 61), 5, 4, 2, 5, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730777', '0123456789', 2, 1, point(30, 60), point(31, 61), 5, 2, 2, 3, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('5c76c35b-98df-481c-ac21-0555c5e51d21', '0123456789', 3, 1, point(30, 60), point(31, 61), 5, 6, 2, 7, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3738888', '0123456789', 4, 1, point(30, 60), point(31, 61), 5, 1, 2, 2, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730779', '0123456789', 1, 1, point(30, 60), point(31, 61), 5, 1, 2, 2, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000');

INSERT INTO state.passengers (
    booking_id,
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    shuttle_lap,
    offer_id,
    dropoff_lap
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', '012345678', 'userid_1', 4, 5, 2, 1, 'acfff773-398f-4913-b9e9-03bf5eda22ac', 2),
    ('acfff773-398f-4913-b9e9-03bf5eda26ac', '012345673', 'userid_1', 4, 1, 2, 2, 'acfff773-398f-4913-b9e9-03bf5eda26ac', 2),
    ('acfff773-398f-4913-b9e9-03bf5eda25ac', '012345670', 'userid_1', 4, 4, 3, 1, 'acfff773-398f-4913-b9e9-03bf5eda25ac', 2),
    ('acfff773-398f-4913-b9e9-03bf5eda24ac', '012345671', 'userid_1', 4, 5, 4, 1, 'acfff773-398f-4913-b9e9-03bf5eda24ac', 2),
    ('acfff773-398f-4913-b9e9-03bf5eda23ac', '012345672', 'userid_1', 4, 2, 4, 2, 'acfff773-398f-4913-b9e9-03bf5eda23ac', 2);

INSERT INTO state.booking_tickets (
    booking_id,
    code,
    status
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', '101', 'issued'),
    ('acfff773-398f-4913-b9e9-03bf5eda26ac', '102', 'issued'),
    ('acfff773-398f-4913-b9e9-03bf5eda25ac', '103', 'issued'),
    ('acfff773-398f-4913-b9e9-03bf5eda24ac', '104', 'issued'),
    ('acfff773-398f-4913-b9e9-03bf5eda23ac', '105', 'issued');

INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    lap,
    begin_stop_id,
    next_stop_id,
    end_lap,
    end_stop_id,
    updated_at,
    advanced_at
)
VALUES
    (1, 3, 3, 3, NULL, NULL, NOW(), NOW()),
    (2, 2, 1, 4, 3,    2, NOW(), NOW()),
    (3, 6, 3, 4, 6,    3, NOW(), NOW()), -- finishing shuttle
    (4, 1, 1, 3, NULL,    NULL, NOW(), NOW()); -- full shuttle
