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
    ya_transport_stop_id,
    is_terminal
)
VALUES (1, 1, 'main_stop', 'stop__123', FALSE),
       (5, 5, 'stop_5', 'stop__5', TRUE);

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
VALUES (
  1,
  1,
  1
), (
  1,
  5,
  2
);

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    ended_at,
    capacity,
    ticket_length,
    work_mode
)
VALUES
(
    1,
    ('dbid_0', 'uuid_0')::db.driver_id,
    1,
    '2020-05-28T11:40:55+0000',
    16,
    3,
    'shuttle_fix'
),
(
    2,
    ('dbid_0', 'uuid_1')::db.driver_id,
    1,
    '2020-05-29T12:40:55+0000',
    16,
    3,
    'shuttle'
),
(
    3,
    ('dbid_0', 'uuid_2')::db.driver_id,
    1,
    '2020-05-28T11:40:55+0000',
    16,
    3,
    'shuttle_fix'
),
(
    4,
    ('dbid_0', 'uuid_3')::db.driver_id,
    1,
    '2020-05-29T12:40:55+0000',
    16,
    3,
    'shuttle'
);

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
('2fef68c9-25d0-4174-9dd0-bdd1b3730775', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 1, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2022-01-24T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730776', '0123456789', 2, 1, point(30, 60), point(31, 61), 1, 1, 1, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2022-01-24T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730777', '0123456789', 3, 1, point(30, 60), point(31, 61), 1, 1, 1, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2022-01-24T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730778', '0123456789', 4, 1, point(30, 60), point(31, 61), 1, 1, 1, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2022-01-24T18:18:00+0000');

ALTER TABLE state.passengers
    DISABLE TRIGGER passenger_ticket_for_booking_trigger
;

INSERT INTO state.passengers (
    booking_id,
    offer_id,
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    locale,
    created_at,
    status,
    ticket,
    finished_at,
    dropoff_lap
)
VALUES
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '0123456789',
    'user_id_1',
    1,
    1,
    5,
    'ru',
    '2020-05-18T15:00:00',
    'finished',
    '0400',
    '2020-05-18T17:00:00',
    1
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    '0123456789',
    'user_id_1',
    2,
    1,
    5,
    'ru',
    '2020-05-18T16:00:00',
    'finished',
    '0401',
    '2020-05-18T19:00:00',
    1
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
    '0123456789',
    'user_id_1',
    3,
    1,
    5,
    'ru',
    '2020-05-18T16:00:00',
    'finished',
    '0401',
    '2020-05-18T19:00:00',
    1
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
    '0123456789',
    'user_id_1',
    4,
    1,
    5,
    'ru',
    '2020-05-18T16:00:00',
    'finished',
    '0401',
    '2020-05-18T19:00:00',
    1
)
;

ALTER TABLE state.passengers
    ENABLE TRIGGER passenger_ticket_for_booking_trigger
;

INSERT INTO state.booking_tickets (
    booking_id,
    code,
    status
) VALUES (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '0400',
    'confirmed'
), (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    '0401',
    'confirmed'
), (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
    '0401',
    'confirmed'
), (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
    '0401',
    'confirmed'
);

INSERT INTO state.feedbacks (
    booking_id,
    choices,
    message,
    created_at
) VALUES (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    ARRAY['choice1', 'choice2'],
    'some_message',
    '2020-05-18T19:00:00'
);

INSERT INTO state.order_billing_requests (
    booking_id,
    "timezone",
    nearest_zone,
    state
) VALUES
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
    'Europe/Moscow',
    'moscow',
    'requested'
), (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
    'Europe/Moscow',
    'moscow',
    'requested'
);

INSERT INTO state.procaas_events (
    booking_id,
    payload
) VALUES
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
    '{}'::JSONB
), (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
    '{}'::JSONB
);
