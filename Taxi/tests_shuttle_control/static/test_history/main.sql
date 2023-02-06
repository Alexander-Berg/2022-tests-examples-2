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
    ya_transport_stop_id
)
VALUES (1, 1, 'main_stop', 'stop__123'),
       (5, 5, 'stop_5', 'stop__5');

INSERT INTO config.routes (
    route_id,
    name,
    is_cyclic
)
VALUES (
    1,
    'main_route',
    false
);

INSERT INTO config.route_points (
    route_id,
    point_id,
    point_order
)
VALUES (1, 1, 1),
       (1, 5, 2);

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
    ('dbid0', 'uuid0')::db.driver_id,
    1,
    16,
    3
),
(
    2,
    ('dbid0', 'uuid1')::db.driver_id,
    1,
    16,
    3
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
    created_at,
    expires_at,
    passengers_count
)
VALUES
('2fef68c9-25d0-4174-9dd0-bdd1b3730775', '0123456789', 1, 1, point(30, 60), point(30, 60), 5, 4, 5, 5, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', 1),
('2fef68c9-25d0-4174-9dd0-bdd1b3730776', '0123456789', 1, 1, point(30, 60), point(30, 60), 5, 4, 5, 5, '(5,RUB)', '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', 1);

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
    offer_id,
    dropoff_lap
)
VALUES
(
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '0123456789',
    'user_id_1',
    1,
    1,
    5,
    'ru',
    '2020-07-18T15:00:00',
    'driving',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
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
    '2020-08-18T15:00:00',
    'finished',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    1
)
;

INSERT INTO state.status_change_time (booking_id, status, changed_at) VALUES
    ('2fef68c9-25d0-4174-9dd0-bdd1b3730776', 'transporting', '2020-08-18T13:15:00');

UPDATE state.status_change_time
  SET changed_at = '2020-08-18T15:00:00'
  WHERE booking_id = '2fef68c9-25d0-4174-9dd0-bdd1b3730776' AND status = 'finished';

INSERT INTO archive.points (
    point_id,
    position
)
VALUES (1, point(30, 60)),
       (5, point(30, 60));

INSERT INTO archive.stops (
    stop_id,
    point_id,
    name,
    ya_transport_stop_id
)
VALUES (1, 1, 'main_stop', 'stop__123'),
       (5, 5, 'stop_5', 'stop__5');

INSERT INTO archive.routes (
    route_id,
    name,
    is_cyclic
)
VALUES (
    1,
    'main_route',
    false
);

INSERT INTO archive.prices (route_id, price, currency) VALUES
    (1, 143, 'RUB');

INSERT INTO archive.shuttles
    (shuttle_id, driver_id, route_id, is_fake, capacity, use_external_confirmation_code)
    VALUES
    (137020, ('fc2e7035862a4c8489c40e3b87351575','3f24c1f6064341c08a1e057f6dd4443f'), 1, 'f', 8, FALSE);

INSERT INTO archive.bookings
    (booking_id, yandex_uid, shuttle_id, user_id, pickup_stop_id, dropoff_stop_id, created_at, finished_at, status)
    VALUES
    ('89fe0a27-9a5d-4c73-bfee-f099d7f8488c', '0123456789', 137020, 'bfc17014109f4e15b15eec443da239da', 1, 5, '2020-06-18T15:00:00', '2020-06-18T16:00:00', 'finished'),
    ('7354c0db-dd0c-4aa2-8da2-83cdacfc5a8b', '0123456789', 137020, 'bfc17014109f4e15b15eec443da239da', 5, 1, '2020-05-18T15:00:00', '2020-05-18T16:00:00', 'finished'),
    ('ee3d7564-8340-45dc-a25d-c3ee9deba2d6', '0123456789', 137020, '6c4d3738d56e400683adacd0640be5a8', 1, 5, '2020-04-18T15:00:00', '2020-04-18T16:00:00', 'cancelled'),
    ('ab3d0769-742d-40c8-818b-39d34446c0a9', '0123456789', 137020, '6c4d3738d56e400683adacd0640be5a8', 5, 1, '2020-03-18T15:00:00', '2020-03-18T16:00:00', 'finished');

INSERT INTO archive.status_change_time (booking_id, status, changed_at) VALUES
    ('89fe0a27-9a5d-4c73-bfee-f099d7f8488c', 'created', '2020-08-18T14:00:00'),
    ('89fe0a27-9a5d-4c73-bfee-f099d7f8488c', 'transporting', '2020-06-18T14:24:00'),
    ('89fe0a27-9a5d-4c73-bfee-f099d7f8488c', 'finished', '2020-06-18T15:00:00');

INSERT INTO state.order_point_text_info (booking_id, point_type, full_text, short_text, uri) VALUES
    ('2fef68c9-25d0-4174-9dd0-bdd1b3730776', 'order_point_a', 'full_order_point_A_text', 'short_order_point_A_text', 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'),
    ('2fef68c9-25d0-4174-9dd0-bdd1b3730776', 'order_point_b', 'full_order_point_B_text', 'short_order_point_B_text', 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'),
    ('2fef68c9-25d0-4174-9dd0-bdd1b3730775', 'order_point_a', 'full_order_point_A_text', 'short_order_point_A_text', 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'),
    ('2fef68c9-25d0-4174-9dd0-bdd1b3730775', 'order_point_b', 'full_order_point_B_text', 'short_order_point_B_text', 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2');

INSERT INTO archive.order_point_text_info (booking_id, point_type, full_text, short_text, uri) VALUES
    ('89fe0a27-9a5d-4c73-bfee-f099d7f8488c', 'order_point_a', 'full_order_point_A_text', 'short_order_point_A_text', 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'),
    ('7354c0db-dd0c-4aa2-8da2-83cdacfc5a8b', 'order_point_a', 'full_order_point_A_text', 'short_order_point_A_text', 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'),
    ('ee3d7564-8340-45dc-a25d-c3ee9deba2d6', 'order_point_a', 'full_order_point_A_text', 'short_order_point_A_text', 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'),
    ('ab3d0769-742d-40c8-818b-39d34446c0a9', 'order_point_a', 'full_order_point_A_text', 'short_order_point_A_text', 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'),
    ('89fe0a27-9a5d-4c73-bfee-f099d7f8488c', 'order_point_b', 'full_order_point_B_text', 'short_order_point_B_text', 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'),
    ('7354c0db-dd0c-4aa2-8da2-83cdacfc5a8b', 'order_point_b', 'full_order_point_B_text', 'short_order_point_B_text', 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'),
    ('ee3d7564-8340-45dc-a25d-c3ee9deba2d6', 'order_point_b', 'full_order_point_B_text', 'short_order_point_B_text', 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'),
    ('ab3d0769-742d-40c8-818b-39d34446c0a9', 'order_point_b', 'full_order_point_B_text', 'short_order_point_B_text', 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2');


