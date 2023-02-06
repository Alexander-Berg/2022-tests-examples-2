INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.642933,55.735054)),
    (3, point(37.643129,55.734452)),
    (4, point(37.643148,55.734349)),
    (5, point(37.643055,55.734163)),
    (6, point(37.641628,55.733419));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 3, 'stop2', 'stop__2'),
    (3, 5, 'stop3', 'stop__3'),
    (4, 6, 'stop4', NULL);

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
  (1, 3, 3),
  (1, 4, 4),
  (1, 5, 5),
  (1, 6, 6)
;

INSERT INTO state.shuttles (
    driver_id, route_id, is_fake, capacity, ticket_length
)
VALUES
    (('dbid0', 'uuid0')::db.driver_id, 1, FALSE, 5, 3),
    (('dbid3', 'uuid3')::db.driver_id, 1, FALSE, 3, 3),
    (('dbid5', 'uuid5')::db.driver_id, 1, FALSE, 3, 3);

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
('acfff773-398f-4913-b9e9-03bf5eda25ac', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('acfff773-398f-4913-b9e9-03bf5eda26ac', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('acfff773-398f-4913-b9e9-03bf5eda21ac', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('acfff773-398f-4913-b9e9-03bf5eda22ac', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('acfff773-398f-4913-b9e9-03bf5eda23ac', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('acfff773-398f-4913-b9e9-03bf5eda24ac', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000');

INSERT INTO state.passengers (
    booking_id,
    offer_id,
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    shuttle_lap,
    status,
    dropoff_lap
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda25ac', 'acfff773-398f-4913-b9e9-03bf5eda25ac', '0123456784', 'userid_5', 1, 1, 4, 1, 'transporting', 1),
    ('acfff773-398f-4913-b9e9-03bf5eda26ac', 'acfff773-398f-4913-b9e9-03bf5eda26ac', '0123456785', 'userid_6', 1, 1, 4, 1, 'transporting', 1),
    ('acfff773-398f-4913-b9e9-03bf5eda21ac', 'acfff773-398f-4913-b9e9-03bf5eda21ac', '0123456789', 'userid_1', 2, 2, 4, 1, 'created', 1),
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', 'acfff773-398f-4913-b9e9-03bf5eda22ac', '0123456781', 'userid_2', 2, 1, 2, 1, 'created', 1),
    ('acfff773-398f-4913-b9e9-03bf5eda23ac', 'acfff773-398f-4913-b9e9-03bf5eda23ac', '0123456782', 'userid_3', 2, 2, 4, 1, 'created', 1),
    ('acfff773-398f-4913-b9e9-03bf5eda24ac', 'acfff773-398f-4913-b9e9-03bf5eda24ac', '0123456783', 'userid_4', 2, 1, 4, 1, 'created', 1);

INSERT INTO state.booking_tickets (
    booking_id,
    status,
    code
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda25ac', 'confirmed', '123'),
    ('acfff773-398f-4913-b9e9-03bf5eda26ac', 'confirmed', '124'),
    ('acfff773-398f-4913-b9e9-03bf5eda21ac', 'issued',    '125'),
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', 'issued',    '126'),
    ('acfff773-398f-4913-b9e9-03bf5eda23ac', 'issued',    '127'),
    ('acfff773-398f-4913-b9e9-03bf5eda24ac', 'issued',    '128');

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
    (2, 1, 1, 2, NOW(), NOW()),
    (3, 1, 1, 2, NOW(), NOW());

INSERT INTO state.pauses (
    pause_id,
    shuttle_id,
    pause_requested
) VALUES (
    1,
    3,
    '2020-05-28T12:25:55+0000'
);

UPDATE state.shuttles
SET pause_state = 'requested',
    pause_id = 1
WHERE shuttle_id = 3;
