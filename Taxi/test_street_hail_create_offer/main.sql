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

INSERT INTO config.workshift_templates (
    template_id,
    route_name,
    schedule,
    max_simultaneous_subscriptions,
    in_operation_since
) VALUES (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             'route1',
             '{
               "timezone":"UTC",
               "intervals": [{
                 "exclude": false,
                 "day": [1, 2, 3, 4, 5, 6, 7]
               }, {
                 "exclude": false,
                 "daytime": [{
                   "from": "16:00:00",
                   "to": "18:30:00"
                 }
                 ]
               }]}'::JSONB,
             10,
             '2019-09-11T10:00:00+0000'
         ),
         (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
             'route1',
             '{
               "timezone":"UTC",
               "intervals": [{
                 "exclude": false,
                 "day": [1, 2, 3, 4, 5, 6, 7]
               }, {
                 "exclude": false,
                 "daytime": [{
                   "from": "16:00:00",
                   "to": "23:30:00"
                 }
                 ]
               }]}'::JSONB,
             10,
             '2019-09-11T10:00:00+0000'
         )
;

INSERT INTO config.workshifts (
    template_id,
    workshift_id,
    route_name,
    work_time,
    created_at,
    max_simultaneous_subscriptions
) VALUES (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             'route1',
             '[2020-01-17 16:00, 2020-01-17 18:20]'::TSRANGE,
             '2019-09-14T09:00:00+0000',
             10
         ),
         (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
             '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
             'route1',
             '[2020-01-17 16:00, 2020-01-17 23:30]'::TSRANGE,
             '2019-09-14T09:00:00+0000',
             10
         )
;

INSERT INTO state.drivers_workshifts_subscriptions (
    subscription_id,
    workshift_id,
    driver_id,
    status,
    subscribed_at
) VALUES (
             1,
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             ('dbid_4', 'uuid_4')::db.driver_id,
             'ongoing',
             '2019-09-14T09:30:00+0000'
         ),
         (
             2,
             '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
             ('dbid_1', 'uuid_1')::db.driver_id,
             'ongoing',
             '2019-09-14T09:30:00+0000'
         )
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
    (1, 6, 6),
    (1, 7, 7);

INSERT INTO state.shuttles (
    driver_id, route_id, is_fake, capacity, ticket_length, subscription_id
)
VALUES
    (('dbid0', 'uuid0')::db.driver_id, 1, FALSE, 4, 3, NULL),
    (('dbid1', 'uuid1')::db.driver_id, 1, FALSE, 4, 3, 2),
    (('dbid2', 'uuid2')::db.driver_id, 1, FALSE, 4, 3, NULL),
    (('dbid3', 'uuid3')::db.driver_id, 1, FALSE, 4, 3, NULL),
    (('dbid4', 'uuid4')::db.driver_id, 1, FALSE, 4, 3, 1);

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
    ('acfff773-398f-4913-b9e9-03bf5eda11ac', '012345618', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('acfff773-398f-4913-b9e9-03bf5eda12ac', '012345613', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('acfff773-398f-4913-b9e9-03bf5eda13ac', '012345612', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('acfff773-398f-4913-b9e9-03bf5eda14ac', '012345614', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', '012345678', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('acfff773-398f-4913-b9e9-03bf5eda26ac', '012345673', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('acfff773-398f-4913-b9e9-03bf5eda25ac', '012345670', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('acfff773-398f-4913-b9e9-03bf5eda24ac', '012345671', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
    ('acfff773-398f-4913-b9e9-03bf5eda23ac', '012345672', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000');

INSERT INTO state.passengers (
    booking_id,
    offer_id,
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    shuttle_lap,
    dropoff_lap
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda11ac', 'acfff773-398f-4913-b9e9-03bf5eda11ac', '012345618', 'userid_1', 1, 5, 2, 3, 4),
    ('acfff773-398f-4913-b9e9-03bf5eda12ac', 'acfff773-398f-4913-b9e9-03bf5eda12ac', '012345613', 'userid_1', 1, 1, 2, 3, 3),
    ('acfff773-398f-4913-b9e9-03bf5eda13ac', 'acfff773-398f-4913-b9e9-03bf5eda13ac', '012345612', 'userid_1', 1, 3, 2, 3, 4),
    ('acfff773-398f-4913-b9e9-03bf5eda14ac', 'acfff773-398f-4913-b9e9-03bf5eda14ac', '012345614', 'userid_1', 1, 5, 4, 3, 4),
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', 'acfff773-398f-4913-b9e9-03bf5eda22ac', '012345678', 'userid_1', 4, 5, 2, 1, 2),
    ('acfff773-398f-4913-b9e9-03bf5eda26ac', 'acfff773-398f-4913-b9e9-03bf5eda26ac', '012345673', 'userid_1', 4, 1, 2, 2, 2),
    ('acfff773-398f-4913-b9e9-03bf5eda25ac', 'acfff773-398f-4913-b9e9-03bf5eda25ac', '012345670', 'userid_1', 4, 4, 3, 1, 2),
    ('acfff773-398f-4913-b9e9-03bf5eda24ac', 'acfff773-398f-4913-b9e9-03bf5eda24ac', '012345671', 'userid_1', 4, 5, 4, 1, 2),
    ('acfff773-398f-4913-b9e9-03bf5eda23ac', 'acfff773-398f-4913-b9e9-03bf5eda23ac', '012345672', 'userid_1', 4, 2, 4, 2, 2);

INSERT INTO state.booking_tickets (
    booking_id,
    code,
    status
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda11ac', '111', 'issued'),
    ('acfff773-398f-4913-b9e9-03bf5eda12ac', '112', 'issued'),
    ('acfff773-398f-4913-b9e9-03bf5eda13ac', '113', 'issued'),
    ('acfff773-398f-4913-b9e9-03bf5eda14ac', '114', 'issued'),
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
    (5, 3, 3, 3, NULL, NULL, NOW(), NOW()),
    (2, 2, 1, 4, 3,    2, NOW(), NOW()),
    (3, 6, 3, 4, 6,    3, NOW(), NOW()), -- finishing shuttle
    (4, 1, 1, 3, NULL,    NULL, NOW(), NOW()); -- full shuttle
