INSERT INTO config.points (
    point_id,
    position
)
VALUES (1, point(30.1, 60)),
       (2, point(37.534406, 55.750028)),
       (3, point(30.3, 60)),
       (4, point(30.4, 60)),
       (5, point(37.583957, 55.750332)),
	   (6, point(37.583957, 55.752332));

INSERT INTO config.stops (
    stop_id,
    point_id,
    name,
    ya_transport_stop_id
)
VALUES (1, 1, 'stop_1', 'stop__1'),
       (2, 2, 'main_stop', 'stop_123'),
       (3, 3, 'stop_3', 'stop__3'),
       (4, 4, 'stop_4', 'stop__4'),
       (5, 5, 'stop_5', 'stop__5'),
	   (6, 6, 'stop_6', 'stop__6');

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
       (1, 3, 3),
       (1, 4, 4),
       (1, 5, 5),
	   (1, 6, 6);

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
	ticket_length,
	ticket_check_enabled,
    capacity
)
VALUES
(
    1,
    ('dbid_0', 'uuid_0')::db.driver_id,
    1,
	10,
	TRUE,
    16
),
(
    2,
    ('park_01', 'uuid_1')::db.driver_id,
    1,
	10,
	TRUE,
    16
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
('2fef68c9-25f0-4174-9fd0-bdd1b3730776', 2, point(37.534406, 55.750028), point(37.534406, 55.750028), 1, 1, 1, 2, (0.5, 'USD')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1),
('2fef68c9-25a0-4174-9ad0-bdd1b3730776', 2, point(37.534406, 55.750028), point(37.534406, 55.750028), 1, 1, 1, 2, (0.5, 'USD')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1),
('2fef68c9-25e0-4174-9ed0-bdd1b3730776', 2, point(37.534406, 55.750028), point(37.534406, 55.750028), 1, 1, 1, 2, (0.5, 'USD')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1),
('2fef68c9-25b0-4174-9bd0-bdd1b3730776', 2, point(37.534406, 55.750028), point(37.534406, 55.750028), 1, 1, 1, 2, (0.5, 'USD')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1),
('2fef68c9-25a0-4174-9bd0-bdd1a3730776', 2, point(37.534406, 55.750028), point(37.534406, 55.750028), 1, 1, 1, 2, (0.5, 'USD')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1);

ALTER TABLE state.passengers
    DISABLE TRIGGER passenger_ticket_for_booking_trigger
;

INSERT INTO state.passengers (
    booking_id,
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    locale,
    created_at,
	ticket,
    status,
    offer_id,
    dropoff_lap
)
VALUES
(
    '2fef68c9-25f0-4174-9fd0-bdd1b3730776',
    '0123456710',
    'user_id_8',
    2,
    2,
    5,
    'ru',
    '2020-05-18T17:00:00',
	'ticket_u8_1',
    'transporting',
    '2fef68c9-25f0-4174-9fd0-bdd1b3730776',
    1
),
(
    '2fef68c9-25a0-4174-9ad0-bdd1b3730776',
    '0123456700',
    'user_id_5',
    2,
    1,
    3,
    'ru',
    '2020-05-18T16:50:00',
	'ticket_u5_1',
    'transporting',
    '2fef68c9-25a0-4174-9ad0-bdd1b3730776',
    1
),
(
    '2fef68c9-25e0-4174-9ed0-bdd1b3730776',
    '0123456701',
    'user_id_6',
    2,
    4,
    6,
    'ru',
    '2020-05-18T17:20:00',
	'ticket_u6_1',
    'transporting',
    '2fef68c9-25e0-4174-9ed0-bdd1b3730776',
    1
),
(
    '2fef68c9-25b0-4174-9bd0-bdd1b3730776',
    '0123456702',
    'user_id_7',
    2,
    3,
    4,
    'ru',
    '2020-05-18T17:15:00',
	'ticket_u7_1',
    'transporting',
    '2fef68c9-25b0-4174-9bd0-bdd1b3730776',
    1
),
(
    '2fef68c9-25a0-4174-9bd0-bdd1a3730776',
    '0123456703',
    'user_id_9',
    2,
    1,
    2,
    'ru',
    '2020-05-18T16:45:00',
	'ticket_u9_1',
    'transporting',
    '2fef68c9-25a0-4174-9bd0-bdd1a3730776',
    1
)
;

INSERT INTO state.booking_tickets (
    booking_id,
    code,
    status
) VALUES (
    '2fef68c9-25f0-4174-9fd0-bdd1b3730776',
    'ticket_u8_1',
    'confirmed'
),
(
    '2fef68c9-25a0-4174-9ad0-bdd1b3730776',
    'ticket_u5_1',
    'confirmed'
),
(
    '2fef68c9-25e0-4174-9ed0-bdd1b3730776',
    'ticket_u6_1',
    'confirmed'
),
(
    '2fef68c9-25b0-4174-9bd0-bdd1b3730776',
    'ticket_u7_1',
    'confirmed'
),
(
    '2fef68c9-25a0-4174-9bd0-bdd1a3730776',
    'ticket_u9_1',
    'confirmed'
)
;

ALTER TABLE state.passengers
    ENABLE TRIGGER passenger_ticket_for_booking_trigger
;

INSERT INTO archive.points (
    point_id,
    position
)
VALUES (2, point(37.583957, 55.752432)),
       (3, point(37.581, 55.754)),
       (4, point(37.582, 55.754)),
       (5, point(37.586, 55.754)),
       (6, point(37.584, 55.754)),
	   (7, point(37.583957, 55.752532));

INSERT INTO archive.stops (
    stop_id,
    point_id,
    name,
    ya_transport_stop_id
)
VALUES (2, 2, 'archive_stop_2', 'stop__1234'),
       (3, 3, 'archive_main_stop', 'stop__56'),
       (4, 4, 'archive_stop_4', 'stop__57'),
       (5, 5, 'archive_stop_5', 'stop__58'),
       (6, 6, 'archive_stop_6', 'stop__59'),
	   (7, 7, 'archive_stop_7', 'stop_66');

INSERT INTO archive.routes (
    route_id,
    name,
	is_cyclic
)
VALUES (
    2,
    'archive_main_route',
	TRUE
);

INSERT INTO archive.route_points (
    route_id,
    point_id,
    point_order
)
VALUES (2, 2, 1),
       (2, 3, 2),
       (2, 4, 3),
       (2, 5, 4),
       (2, 6, 5),
	   (2, 7, 6);

INSERT INTO archive.shuttles (
    shuttle_id,
    driver_id,
    route_id,
	is_fake,
	capacity,
    use_external_confirmation_code
)
VALUES
(
    2,
    ('dbid_1', 'uuid_0')::db.driver_id,
    2,
	FALSE,
	16,
    FALSE
),
(
    3,
    ('park_01', 'uuid_1')::db.driver_id,
    2,
	FALSE,
	16,
    FALSE
);


INSERT INTO archive.matching_offers(
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
    (
        '2fef68d7-25d0-4174-9dd0-bdd1b3730776',
        2,
        point(37.534406, 55.750028),
        point(37.534406, 55.750028),
        2,
        1,
        2,
        2,
        (0.5, 'USD')::db.trip_price,
        '2022-01-20T16:00:00+0000',
        '2020-01-20T16:48:00+0000',
        2
    ),
    (
        '2fef68e7-25d0-4174-9dd0-bdd1b3730776',
        2,
        point(37.534406, 55.750028),
        point(37.534406, 55.750028),
        2,
        1,
        2,
        2,
        (0.5, 'USD')::db.trip_price,
        '2022-01-20T16:00:00+0000',
        '2020-01-20T16:48:00+0000',
        2
    ),
    (
        '2fef68f7-25d0-4174-9dd0-bdd1b3730776',
        2,
        point(37.534406, 55.750028),
        point(37.534406, 55.750028),
        2,
        1,
        2,
        2,
        (0.5, 'USD')::db.trip_price,
        '2022-01-20T16:00:00+0000',
        '2020-01-20T16:48:00+0000',
        2
    ),
    (
        '2fef68f7-25e0-4174-9dd0-add1b3730776',
        2,
        point(37.534406, 55.750028),
        point(37.534406, 55.750028),
        2,
        1,
        2,
        2,
        (0.5, 'USD')::db.trip_price,
        '2022-01-20T16:00:00+0000',
        '2020-01-20T16:48:00+0000',
        2
    ),
    (
        '2aea68f7-25e0-4174-9dd0-add1b3730776',
        2,
        point(37.534406, 55.750028),
        point(37.534406, 55.750028),
        2,
        1,
        2,
        2,
        (0.5, 'USD')::db.trip_price,
        '2022-01-20T16:00:00+0000',
        '2020-01-20T16:48:00+0000',
        2
    ),
    (
        '2aea68f7-25a0-4174-9df0-add1b3730776',
        2,
        point(37.534406, 55.750028),
        point(37.534406, 55.750028),
        2,
        1,
        2,
        2,
        (0.5, 'USD')::db.trip_price,
        '2022-01-20T16:00:00+0000',
        '2020-01-20T16:48:00+0000',
        2
    );

INSERT INTO archive.bookings (
    booking_id,
    yandex_uid,
    user_id,
    shuttle_id,
    pickup_stop_id,
    dropoff_stop_id,
    created_at,
	finished_at,
	ticket,
    status,
	shuttle_lap,
    offer_id
)
VALUES
(
    '2fef68d7-25d0-4174-9dd0-bdd1b3730776',
    '0123456620',
    'user_id_10',
    3,
    5,
    3,
    '2020-05-18T15:30:00',
    '2020-05-18T15:37:00',
	'ticket_u10_1',
    'finished',
	2,
    '2fef68d7-25d0-4174-9dd0-bdd1b3730776'
),
(
    '2fef68e7-25d0-4174-9dd0-bdd1b3730776',
    '0123456621',
    'user_id_11',
    3,
    7,
    2,
    '2020-05-18T15:30:00',
    '2020-05-18T15:37:00',
	'ticket_u11_1',
    'finished',
	2,
    '2fef68e7-25d0-4174-9dd0-bdd1b3730776'
),
(
    '2fef68f7-25d0-4174-9dd0-bdd1b3730776',
    '0123456622',
    'user_id_12',
    3,
    2,
    4,
    '2020-05-18T15:30:00',
    '2020-05-18T15:37:00',
	'ticket_u12_1',
    'finished',
	3,
    '2fef68f7-25d0-4174-9dd0-bdd1b3730776'
),
(
    '2fef68f7-25e0-4174-9dd0-add1b3730776',
    '0123456623',
    'user_id_13',
    3,
    5,
    7,
    '2020-05-18T15:30:00',
    '2020-05-18T15:37:00',
	'ticket_u13_1',
    'finished',
	2,
    '2fef68f7-25e0-4174-9dd0-add1b3730776'
),
(
    '2aea68f7-25e0-4174-9dd0-add1b3730776',
    '0123456624',
    'user_id_14',
    3,
    2,
    3,
    '2020-05-18T15:30:00',
    '2020-05-18T15:37:00',
	'ticket_u14_1',
    'finished',
	2,
    '2aea68f7-25e0-4174-9dd0-add1b3730776'
),
(
    '2aea68f7-25a0-4174-9df0-add1b3730776',
    '0123456625',
    'user_id_15',
    3,
    7,
    6,
    '2020-05-18T15:30:00',
    '2020-05-18T15:37:00',
	'ticket_u15_1',
    'finished',
	1,
    '2aea68f7-25a0-4174-9df0-add1b3730776'
)
;

INSERT INTO archive.booking_tickets (
    booking_id,
    code,
    status
) VALUES (
    '2fef68d7-25d0-4174-9dd0-bdd1b3730776',
    'ticket_u10_1',
    'confirmed'
), (
    '2fef68e7-25d0-4174-9dd0-bdd1b3730776',
    'ticket_u11_1',
    'confirmed'
), (
    '2fef68f7-25d0-4174-9dd0-bdd1b3730776',
    'ticket_u12_1',
    'confirmed'
),
(
    '2fef68f7-25e0-4174-9dd0-add1b3730776',
    'ticket_u13_1',
    'confirmed'
), (
    '2aea68f7-25e0-4174-9dd0-add1b3730776',
    'ticket_u14_1',
    'confirmed'
), (
    '2aea68f7-25a0-4174-9df0-add1b3730776',
    'ticket_u15_1',
    'confirmed'
)
;

INSERT INTO archive.prices (
	route_id,
	price,
	currency
)
VALUES
(
	2,
	0.5,
	'USD'
);

INSERT INTO archive.status_change_time (
    booking_id,
    changed_at,
    status
) VALUES
    ('2fef68d7-25d0-4174-9dd0-bdd1b3730776', '2020-05-18T15:37:00', 'finished'),
    ('2fef68d7-25d0-4174-9dd0-bdd1b3730776', '2020-05-18T15:30:00', 'created');
