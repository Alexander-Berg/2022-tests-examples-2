INSERT INTO config.points (
    point_id,
    position
)
VALUES (1, point(37.534406, 55.750028)),
       (5, point(37.583957, 55.750332)),
	   (6, point(37.642474, 55.735525));

INSERT INTO config.stops (
    stop_id,
    point_id,
    name,
    ya_transport_stop_id
)
VALUES (1, 1, 'main_stop', 'stop__123'),
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
       (1, 5, 2),
	   (1, 6, 3);

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
    (
        '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        1,
        point(37.534406, 55.750028),
        point(37.534406, 55.750028),
        1,
        1,
        1,
        2,
        (40.5, 'RUB')::db.trip_price,
        '2022-01-20T16:00:00+0000',
        '2020-01-20T16:48:00+0000',
        1
    ),
    (
        '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
        1,
        point(37.534406, 55.750028),
        point(37.534406, 55.750028),
        1,
        1,
        1,
        2,
        (40.5, 'RUB')::db.trip_price,
        '2022-01-20T16:00:00+0000',
        '2020-01-20T16:48:00+0000',
        1
    );

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
    finished_at,
    ticket,
    status,
    app_version,
    app_platform,
    offer_id,
    dropoff_lap
)
VALUES
('2fef68c9-25d0-4174-9dd0-bdd1b3730775', '0123456789', 'user_id_1', 1, 5, 6, 'ru', '2020-05-18T15:00:00', '2020-05-18T15:10:00', 'ticket_u1_1', 'finished', '4.8.1.0', 'android', '2fef68c9-25d0-4174-9dd0-bdd1b3730775', 1),
('2fef68c9-25d0-4174-9dd0-bdd1b3730776', '0123456789', 'user_id_1', 2, 1, 5, 'ru', '2020-05-18T16:00:00', '2020-05-18T16:12:00', 'ticket_u1_2', 'driving', '4.8.1.0', 'android', '2fef68c9-25d0-4174-9dd0-bdd1b3730776', 1);

INSERT INTO state.booking_tickets (
    booking_id,
    code,
    status
)
VALUES
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    'ticket_u1_1',
    'confirmed'
),
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    'ticket_u1_2',
    'issued'
)
;

ALTER TABLE state.passengers
    ENABLE TRIGGER passenger_ticket_for_booking_trigger
;

INSERT INTO archive.points (
    point_id,
    position
)
VALUES (2, point(37.587093, 55.733974)),
       (6, point(37.462541, 55.699548)),
	   (7, point(37.618136, 55.752249));

INSERT INTO archive.stops (
    stop_id,
    point_id,
    name,
    ya_transport_stop_id
)
VALUES (2, 2, 'archive_main_stop', 'stop__1234'),
       (6, 6, 'archive_stop_5', 'stop__56'),
	   (7, 7, 'archive_stop_6', 'stop_66');

INSERT INTO archive.routes (
    route_id,
    name,
	is_cyclic,
    version
)
VALUES (
    2,
    'archive_main_route',
	FALSE,
    1
);

INSERT INTO archive.route_points (
    route_id,
    point_id,
    point_order
)
VALUES (2, 2, 1),
       (2, 6, 2),
	   (2, 7, 3);

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
        '2fef68c0-25d0-4174-9dd0-bdd1b3730775',
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
        '2fef68c7-25d0-4174-9dd0-bdd1b3730776',
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
    app_version,
    app_platform,
    offer_id
)
VALUES
(
    '2fef68c0-25d0-4174-9dd0-bdd1b3730775',
    '0123456777',
    'user_id_2',
    2,
    2,
    6,
    '2020-05-18T14:30:00',
    '2020-05-18T14:39:00',
	'ticket_u2_1',
    'finished',
    '4.8.1.0',
    'android',
    '2fef68c0-25d0-4174-9dd0-bdd1b3730775'
),
(
    '2fef68c7-25d0-4174-9dd0-bdd1b3730776',
    '0123456666',
    'user_id_3',
    3,
    6,
    7,
    '2020-05-18T15:30:00',
    '2020-05-18T15:37:00',
	'ticket_u3_1',
    'finished',
    '4.8.1.0',
    'android',
    '2fef68c7-25d0-4174-9dd0-bdd1b3730776'
)
;

INSERT INTO archive.booking_tickets (
    booking_id,
    code,
    status
) VALUES (
    '2fef68c0-25d0-4174-9dd0-bdd1b3730775',
    'ticket_u2_1',
    'confirmed'
), (
    '2fef68c7-25d0-4174-9dd0-bdd1b3730776',
    'ticket_u3_1',
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
    ('2fef68c7-25d0-4174-9dd0-bdd1b3730776', '2020-05-18T15:37:00', 'finished'),
    ('2fef68c7-25d0-4174-9dd0-bdd1b3730776', '2020-05-18T15:30:00', 'created'),
    ('2fef68c7-25d0-4174-9dd0-bdd1b3730776', '2020-05-18T15:32:00', 'transporting');
