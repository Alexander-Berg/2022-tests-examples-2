INSERT INTO config.points (
    point_id,
    position
)
VALUES (1, point(30.002, 60.002)),
       (5, point(30.008, 60.008));

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
VALUES (1, 'main_route'),
       (2, 'second_route');

INSERT INTO config.route_points (
    route_id,
    point_id,
    point_order
)
VALUES (1, 1, 1),
       (1, 5, 2),
       (2, 1, 1),
       (2, 5, 2);

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    capacity,
    ticket_length,
    vfh_id
)
VALUES
(
    1,
    ('dbid_0', 'uuid_0')::db.driver_id,
    1,
    16,
    4,
    NULL
),
(
    2,
    ('dbid_0', 'uuid_1')::db.driver_id,
    1,
    16,
    4,
    '1234567890'
);

ALTER TABLE state.passengers
    DISABLE TRIGGER passenger_ticket_for_booking_trigger
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
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    NULL,
    1,
    1,
    point(30, 60),
    point(31, 61),
    1,
    1,
    5,
    1,
    '(0,RUB)',
    1,
    '2020-01-17T18:00:00+0000',
    '2020-01-17T18:18:00+0000'
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    NULL,
    2,
    1,
    point(30, 60),
    point(31, 61),
    1,
    1,
    5,
    1,
    '(10,RUB)',
    1,
    '2020-01-17T18:00:00+0000',
    '2020-01-17T18:18:00+0000'
);

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
    ticket,
    offer_id,
    cancel_reason,
    finished_at,
    dropoff_lap,
    origin,
    service_origin_id
)
VALUES
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    NULL,
    NULL,
    1,
    1,
    5,
    'ru',
    '2020-05-18T15:00:00',
    'driving',
    '1230',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    NULL,
    '2020-05-18T15:01:00',
    1,
    'service',
    'service_origin_1'
),
(
    'acfff773-398f-4913-b9e9-03bf5eda23ac',
    NULL,
    NULL,
    2,
    1,
    5,
    'ru',
    '2020-05-18T15:00:00',
    'finished',
    '1230',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    NULL,
    '2020-05-18T15:01:00',
    1,
    'service',
    'service_origin_1'
)
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
    (1, 0, 1, 1, NOW(), NOW()),
    (2, 0, 1, 1, NOW(), NOW());

INSERT INTO state.order_point_text_info (
    booking_id,
    point_type,
    full_text,
    short_text,
    uri
)
VALUES (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    'order_point_a',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    'order_point_b',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
  ),
  (
    'acfff773-398f-4913-b9e9-03bf5eda23ac',
    'order_point_a',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
  ),
  (
    'acfff773-398f-4913-b9e9-03bf5eda23ac',
    'order_point_b',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
  );

INSERT INTO state.status_change_time (booking_id, status, changed_at) VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda23ac', 'transporting', '2020-05-18T15:00:00');
