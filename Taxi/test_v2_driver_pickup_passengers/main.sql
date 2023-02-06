INSERT INTO config.points (
    position
)
VALUES (
    point(30, 60)
), (
    point(60, 30)
);

INSERT INTO config.stops (
    point_id,
    name
)
VALUES (
    1,
    'main_stop'
), (
    2,
    'second_stop'
);

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
),
(
   1,
   2,
   2
);

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    capacity,
    ticket_length,
    work_mode,
    use_external_confirmation_code
)
VALUES
    (1, ('dbid_0', 'uuid_0')::db.driver_id, 1, 16, 3, 'shuttle', false),
    (2, ('dbid_1', 'uuid_1')::db.driver_id, 1, 16, 3, 'shuttle', true),
    (3, ('dbid_2', 'uuid_2')::db.driver_id, 1, 16, 3, 'shuttle', true)
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
    (1, 1, 1, 1, NOW(), NOW()),
    (2, 1, 1, 1, NOW(), NOW()),
    (3, 1, 1, 1, NOW(), NOW())
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
    expires_at,
    external_confirmation_code
)
VALUES
('2fef68c9-25d0-4174-9dd0-bdd1b3730775', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', NULL),
('427a330d-2506-464a-accf-346b31e288b9', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', NULL),
('5c76c35b-98df-481c-ac21-0555c5e51d21', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', NULL),
('5c76c35b-98df-481c-ac21-0555c5e51aaa', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+ 0000', NULL),
('2fef68c9-25d0-4174-9dd0-bdd1b3730722', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', NULL),
('2fef68c9-25d0-4174-9dd0-bdd1b3730000', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', NULL),
('2fef68c9-25d0-4174-9dd0-bdd1b373077f', NULL, 2, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', '1111'),
('427a330d-2506-464a-accf-346b31e288bf', NULL, 2, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', '2222'),
('5c76c35b-98df-481c-ac21-0555c5e51d2f', NULL, 2, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', '3333'),
('5c76c35b-98df-481c-ac21-0555c5e51aaf', NULL, 2, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', '4224'), -- wrong code
('2fef68c9-25d0-4174-9dd0-bdd1b373072f', NULL, 2, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', '4444'),
('2fef68c9-25d0-4174-9dd0-bdd1b373000f', NULL, 2, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', '5555'),
('2fef68c9-25d0-4174-9dd0-bdd1b373000a', NULL, 2, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', '5555'),
('2fef68c9-25d0-4174-9dd0-bdd1b373077e', NULL, 2, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 3, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000', '8888');

ALTER TABLE state.passengers
    DISABLE TRIGGER passenger_ticket_for_booking_trigger
;


INSERT INTO state.passengers (
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    booking_id,
    dropoff_stop_id,
    status,
    ticket,
    finished_at,
    offer_id,
    dropoff_lap,
    origin,
    service_origin_id
)
VALUES (
           '0000000000',
           'user_id_0',
           1,
           1,
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           2,
           'created',
           '9999',
           NULL,
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            1,
           'application',
           NULL
       ), (
           '1111111111',
           'user_id_1',
           1,
           1,
           '427a330d-2506-464a-accf-346b31e288b9',
           2,
           'transporting',
           '9998',
           NULL,
           '427a330d-2506-464a-accf-346b31e288b9',
            1,
           'application',
           NULL
       ), (
           '2222222222',
           'user_id_2',
           1,
           1,
           '5c76c35b-98df-481c-ac21-0555c5e51d21',
           2,
           'finished',
           '9997',
           '2020-05-18T15:00:00',
           '5c76c35b-98df-481c-ac21-0555c5e51d21',
           1,
           'application',
           NULL
       ), (
           '3333333333',
           'user_id_3',
           2,
           2,
           '5c76c35b-98df-481c-ac21-0555c5e51aaa',
           2,
           'created',
           '9996',
           NULL,
           '5c76c35b-98df-481c-ac21-0555c5e51aaa',
           1,
           'application',
           NULL
       ), (
           '4444444444',
           'user_id_4',
           1,
           1,
           '2fef68c9-25d0-4174-9dd0-bdd1b3730722',
           2,
           'created',
           '9995',
           NULL,
           '2fef68c9-25d0-4174-9dd0-bdd1b3730722',
           1,
           'application',
           NULL
       ), (
           '5555555555',
           'user_id_5',
           1,
           1,
           '2fef68c9-25d0-4174-9dd0-bdd1b3730000',
           2,
           'finished',
           '9994',
           '2020-05-18T15:00:00',
           '2fef68c9-25d0-4174-9dd0-bdd1b3730000',
           1,
           'application',
           NULL
       ), (
           NULL,
           NULL,
           2,
           1,
           '2fef68c9-25d0-4174-9dd0-bdd1b373077f',
           2,
           'created',
           '1999',
           NULL,
           '2fef68c9-25d0-4174-9dd0-bdd1b373077f',
           1,
           'service',
           'moscow_bus'
       ), (
           NULL,
           NULL,
           2,
           1,
           '427a330d-2506-464a-accf-346b31e288bf',
           2,
           'transporting',
           '1998',
           NULL,
           '427a330d-2506-464a-accf-346b31e288bf',
           1,
           'service',
           'moscow_bus'
       ), (
           NULL,
           NULL,
           2,
           1,
           '5c76c35b-98df-481c-ac21-0555c5e51d2f',
           2,
           'finished',
           '9997',
           '2020-05-18T15:00:00',
           '5c76c35b-98df-481c-ac21-0555c5e51d2f',
           1,
           'service',
           'moscow_bus'
       ), (
           NULL,
           NULL,
           2,
           1,
           '5c76c35b-98df-481c-ac21-0555c5e51aaf',
           2,
           'created',
           '1996',
           NULL,
           '5c76c35b-98df-481c-ac21-0555c5e51aaf',
           1,
           'service',
           'moscow_bus'
       ), (
           NULL,
           NULL,
           3,
           1,
           '2fef68c9-25d0-4174-9dd0-bdd1b373072f',
           2,
           'created',
           '1997',
           '2020-05-18T15:00:00',
           '2fef68c9-25d0-4174-9dd0-bdd1b373072f',
           1,
           'service',
           'moscow_bus'
       ), (
           NULL,
           NULL,
           2,
           1,
           '2fef68c9-25d0-4174-9dd0-bdd1b373000f',
           2,
           'created',
           '1994',
           NULL,
           '2fef68c9-25d0-4174-9dd0-bdd1b373000f',
           1,
           'service',
           'moscow_bus'
       ), (
           NULL,
           NULL,
           2,
           1,
           '2fef68c9-25d0-4174-9dd0-bdd1b373000a',
           2,
           'finished',
           '2994',
           '2020-05-18T15:00:00',
           '2fef68c9-25d0-4174-9dd0-bdd1b373000a',
           1,
           'service',
           'moscow_bus'
       ), (
           NULL,
           NULL,
           2,
           1,
           '2fef68c9-25d0-4174-9dd0-bdd1b373077e',
           2,
           'created',
           '2999',
           NULL,
           '2fef68c9-25d0-4174-9dd0-bdd1b373077e',
           1,
           'service',
           'moscow_bus'
       );

ALTER TABLE state.passengers
    ENABLE TRIGGER passenger_ticket_for_booking_trigger
;

INSERT INTO state.booking_tickets (
    booking_id,
    code,
    status
) VALUES (
   '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
   '0101',
   'issued'
), (
   '427a330d-2506-464a-accf-346b31e288b9',
   '0202',
   'confirmed'
), (
   '5c76c35b-98df-481c-ac21-0555c5e51d21',
   '0303',
   'confirmed'
), (
   '5c76c35b-98df-481c-ac21-0555c5e51aaa',
   '0404',
   'confirmed'
), (
   '2fef68c9-25d0-4174-9dd0-bdd1b3730722',
   '0505',
   'issued'
), (
   '2fef68c9-25d0-4174-9dd0-bdd1b3730000',
   '0505',
   'confirmed'
), (
    '2fef68c9-25d0-4174-9dd0-bdd1b373077f',
    '0707',
    'issued'
), (
 '427a330d-2506-464a-accf-346b31e288bf',
 '0808',
 'confirmed'
), (
 '5c76c35b-98df-481c-ac21-0555c5e51d2f',
 '0909',
 'confirmed'
), (
 '2fef68c9-25d0-4174-9dd0-bdd1b373072f',
 '1010',
 'confirmed'
), (
 '2fef68c9-25d0-4174-9dd0-bdd1b373000f',
 '1212',
 'issued'
), (
 '2fef68c9-25d0-4174-9dd0-bdd1b373000a',
 '1222',
 'confirmed'
), (
 '2fef68c9-25d0-4174-9dd0-bdd1b373077e',
 '8888',
 'issued'
), (
 '2fef68c9-25d0-4174-9dd0-bdd1b373077e',
 '8889',
 'issued'
), (
 '2fef68c9-25d0-4174-9dd0-bdd1b373077e',
 '8887',
 'issued'
);
