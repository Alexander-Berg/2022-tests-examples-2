INSERT INTO config.points (
    point_id,
    position
)
VALUES (1, point(30, 60)),
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
VALUES (
    1,
    'main_route'
), (
    2,
    'second_route'
);

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
    ticket_length
)
VALUES
(
    1,
    ('dbid_0', 'uuid_0')::db.driver_id,
    1,
    16,
    4
),
(
    2,
    ('dbid_0', 'uuid_1')::db.driver_id,
    1,
    16,
    4
),
(
    3,
    ('dbid_0', 'uuid_2')::db.driver_id,
    2,
    16,
    4
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
('2fef68c9-25d0-4174-9dd0-bdd1b3730774', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730775', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(0,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730776', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730777', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730778', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730779', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730780', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730781', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730782', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730783', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730784', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730785', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730786', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730787', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 5, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000');

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
    dropoff_lap
)
VALUES
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730769',
    '0123456722',
    'user_id_1',
    1,
    1,
    5,
    'ru',
    '2020-05-18T15:00:00',
    'finished',
    '1230',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730774',
    NULL,
    '2020-05-18T15:01:00',
    1
),
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
    '1230',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    NULL,
    '2020-05-18T15:01:00',
    1
),
(
    'acfff773-398f-4913-b9e9-03bf5eda23ac',
    '0123456789',
    'user_id_1',
    1,
    1,
    5,
    'ru',
    '2020-05-18T15:00:00',
    'finished',
    '1230',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    NULL,
    '2020-05-18T15:01:00',
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
    '1240',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
    NULL,
    NULL,
    1
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
    'legacy_client',
    'user_id_1',
    2,
    1,
    5,
    'ru',
    '2020-05-18T16:00:00',
    'driving',
    '1524',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
    NULL,
    NULL,
    1
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
    '0123456787',
    'user_id_1',
    2,
    1,
    5,
    'ru',
    '2020-05-18T16:00:00',
    'created',
    '7770',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
    NULL,
    NULL,
    1
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3738888',
    '0123456722',
    'user_id_1',
    3,
    1,
    5,
    'ru',
    '2020-05-18T16:00:00',
    'driving',
    '1524',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730780',
    NULL,
    NULL,
    1
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
    '0123456780',
    'user_id_3',
    3,
    1,
    5,
    'ru',
    '2020-05-18T16:00:00',
    'transporting',
    '1523',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730781',
    NULL,
    NULL,
    1
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730770',
    '0123456722',
    'user_id_1',
    1,
    1,
    5,
    'ru',
    '2020-05-18T15:00:00',
    'cancelled',
    '1230',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730782',
    'by_user',
    '2020-05-18T15:01:00',
    1
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730771',
    '0123456722',
    'user_id_1',
    1,
    1,
    5,
    'ru',
    '2020-05-18T15:00:00',
    'cancelled',
    '1230',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730783',
    'pickup_passed',
    '2020-05-18T15:01:00',
    1
),
(
    '5c76c35b-98df-481c-ac21-0555c5e51d23',
    '0123456722',
    'user_id_1',
    1,
    1,
    5,
    'ru',
    '2020-05-18T15:00:00',
    'cancelled',
    '1230',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730784',
    'by_driver_stop',
    '2020-05-18T15:01:00',
    1
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730773',
    '0123456722',
    'user_id_1',
    1,
    1,
    5,
    'ru',
    '2020-05-18T15:00:00',
    'cancelled',
    '1230',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730785',
    'fake_stale_shuttle',
    '2020-05-18T15:01:00',
    1
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730774',
    '0123456722',
    'user_id_1',
    1,
    1,
    5,
    'ru',
    '2020-05-18T15:00:00',
    'cancelled',
    '1230',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730786',
    'by_driver_stop',
    '2020-05-18T15:01:00',
    1
),
(
    'acfff773-398f-4913-b9e9-03bf5eda26ac',
    '0123456722',
    'user_id_1',
    1,
    1,
    5,
    'ru',
    '2020-05-18T13:00:00',
    'cancelled',
    '1230',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730787',
    'by_driver_stop',
    '2020-05-18T13:01:00',
    1
)
;

INSERT INTO state.feedbacks (
    booking_id,
    choices,
    "message",
    created_at
) VALUES (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730774',
    ARRAY[]::TEXT[],
    '',
    '2020-05-18T15:00:00'
);

ALTER TABLE state.passengers
    ENABLE TRIGGER passenger_ticket_for_booking_trigger
;

INSERT INTO state.booking_tickets (
    booking_id,
    status,
    code
)
VALUES
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    'confirmed',
    '1230'
),
(
    'acfff773-398f-4913-b9e9-03bf5eda23ac',
    'confirmed',
    '1230'
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    'issued',
    '1240'
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
    'issued',
    '1524'
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
    'issued',
    '7770'
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3738888',
    'issued',
    '1524'
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
    'confirmed',
    '1523'
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
    (2, 0, 1, 1, NOW(), NOW()),
    (3, 0, 1, 1, NOW(), NOW());

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
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
    'order_point_a',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
    'order_point_b',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
    'order_point_a',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
    'order_point_b',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3738888',
    'order_point_a',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3738888',
    'order_point_b',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    'order_point_a',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    'order_point_b',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730770',
    'order_point_a',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730770',
    'order_point_b',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730771',
    'order_point_a',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730771',
    'order_point_b',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
  ),
  (
    '5c76c35b-98df-481c-ac21-0555c5e51d23',
    'order_point_a',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
  ),
  (
    '5c76c35b-98df-481c-ac21-0555c5e51d23',
    'order_point_b',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730773',
    'order_point_a',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730773',
    'order_point_b',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730774',
    'order_point_a',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
  ),
  (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730774',
    'order_point_b',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
  ),
  (
    'acfff773-398f-4913-b9e9-03bf5eda26ac',
    'order_point_a',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
  ),
  (
    'acfff773-398f-4913-b9e9-03bf5eda26ac',
    'order_point_b',
    'full_text',
    'text',
    'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
  );

