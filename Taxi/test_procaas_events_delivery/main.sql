INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(37.50, 55.75)),
    (2, point(37.51, 55.75))
;

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 2, 'stop2', 'stop__2')
;

INSERT INTO config.routes (
    route_id,
    name
)
VALUES
    (1, 'route1')
;

INSERT INTO config.route_points (
    route_id, point_id, point_order
)
VALUES
    (1, 1, 1),
    (1, 2, 2)
;

INSERT INTO config.workshift_templates (
    template_id,
    route_name,
    schedule,
    max_simultaneous_subscriptions,
    in_operation_since,
    deprecated_since,
    personal_goal,
    generated_up_to
) VALUES ( -- 1
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             'route_1',
             '{
               "timezone":"UTC",
               "intervals": [{
                 "exclude": false,
                 "day": [4]
               }, {
                 "exclude": false,
                 "daytime": [{
                   "from": "10:30:00",
                   "to": "14:00:00"
                 }
                 ]
               }]}'::JSONB,
             10,
             '2020-05-28T10:40:55+0000',
             NULL,
             NULL,
             NULL
         );

INSERT INTO config.workshifts (
    template_id,
    workshift_id,
    route_name,
    work_time,
    created_at,
    in_operation_since,
    max_simultaneous_subscriptions
)
VALUES (
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           '427a330d-2506-464a-accf-346b31e288a9',
           'route_1',
           '[2020-05-28T10:15:00+0000, 2020-05-28T18:00:00+0000]'::tsrange,
           '2020-05-28T10:15:16+0000',
           '2020-05-28T10:15:16+0000',
           10
       ),
       (
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           '427a330d-2506-464a-accf-346b31e288a1',
           'route_1',
           '[2020-05-28T10:15:00+0000, 2020-05-28T11:00:00+0000]'::tsrange,
           '2020-05-28T10:15:16+0000',
           '2020-05-28T10:15:16+0000',
           10
       ),
       (
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           '427a330d-2506-464a-accf-346b31e288a2',
           'route_1',
           '[2020-05-28T12:15:00+0000, 2020-05-28T18:00:00+0000]'::tsrange,
           '2020-05-28T10:15:16+0000',
           '2020-05-28T10:15:16+0000',
           10);

INSERT INTO state.drivers_workshifts_subscriptions (
    subscription_id,
    workshift_id,
    driver_id,
    subscribed_at,
    status
) VALUES (
             3,
             '427a330d-2506-464a-accf-346b31e288a9',
             ('dbid_3', 'uuid_3')::db.driver_id,
             '2020-09-14T10:15:16+0000',
             'ongoing'
         ),
         (
             4,
             '427a330d-2506-464a-accf-346b31e288a1',
             ('dbid_4', 'uuid_4')::db.driver_id,
             '2020-09-14T10:15:16+0000',
             'ongoing'
         ),
         (
             5,
             '427a330d-2506-464a-accf-346b31e288a2',
             ('dbid_5', 'uuid_5')::db.driver_id,
             '2020-09-14T10:15:16+0000',
             'ongoing'
         );

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    capacity,
    ticket_length,
    work_mode,
                            subscription_id
)
VALUES
    (1, ('dbid_1', 'uuid_1')::db.driver_id, 1, 4, 3, 'shuttle_fix', NULL),
    (2, ('dbid_2', 'uuid_2')::db.driver_id, 1, 4, 3, 'shuttle_fix', NULL),
    (3, ('dbid_3', 'uuid_3')::db.driver_id, 1, 4, 3, 'shuttle_fix', 3),
    (4, ('dbid_4', 'uuid_4')::db.driver_id, 1, 4, 3, 'shuttle_fix', 4),
    (5, ('dbid_5', 'uuid_5')::db.driver_id, 1, 4, 3, 'shuttle_fix', 5)
;

INSERT INTO state.shuttle_trip_progress (
    shuttle_id, lap, begin_stop_id, next_stop_id, updated_at, advanced_at, block_reason
)
VALUES
    (1, 1, 1, 2, '2020-05-28T11:30:55+0000', '2020-05-28T11:30:55+0000', 'none'),
    (2, 1, 1, 2, '2020-05-28T09:40:55+0000', '2020-05-28T11:30:55+0000', 'none'),
    (3, 1, 1, 2, '2020-05-28T09:40:55+0000', '2020-05-28T11:30:55+0000', 'none'),
    (4, 1, 1, 2, '2020-05-28T11:30:55+0000', '2020-05-28T11:30:55+0000', 'out_of_workshift'),
    (5, 1, 1, 2, '2020-05-28T11:30:55+0000', '2020-05-28T11:30:55+0000', 'out_of_workshift')
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
('2fef68c9-25d0-4174-9dd0-bdd1b3730775', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('427a330d-2506-464a-accf-346b31e288b9', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('2fef68c9-25d0-4174-9dd0-bdd1b3730776', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('427a330d-2506-464a-accf-346b31e288c9', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000');

INSERT INTO state.passengers (
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    booking_id,
    offer_id,
    status,
    ticket,
    dropoff_lap
)
VALUES (
           '0123456789',
           'userid_1',
           1,
           1,
           2,
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           'driving',
           '123',
            1
       ), (
           '9012345678',
           'userid_2',
           2,
           1,
           2,
           '427a330d-2506-464a-accf-346b31e288b9',
           '427a330d-2506-464a-accf-346b31e288b9',
           'driving',
           '124',
            1
       ),
       (
            '8901234567',
            'userid_3',
            2,
            1,
            2,
            '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
            '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
            'driving',
            '125',
            1
       ),
       (
            '7890123456',
            'userid_4',
            3,
            1,
            2,
            '427a330d-2506-464a-accf-346b31e288c9',
            '427a330d-2506-464a-accf-346b31e288c9',
            'driving',
            '126',
            1
       )
;

INSERT INTO state.procaas_events (
    booking_id,
    payload,
    created_at
) VALUES (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '{}'::JSONB,
    '2020-05-28T11:30:55+0000'
), (
    '427a330d-2506-464a-accf-346b31e288c9',
    '{"foo": false, "bar": true}'::JSONB,
    '2020-05-28T11:30:55+0000'
);
