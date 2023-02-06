INSERT INTO config.points (
    point_id,
    position
)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.642933,55.735054)),
    (3, point(37.643129,55.734452)),
    (4, point(37.643148,55.734349));

INSERT INTO config.stops (
    stop_id,
    point_id,
    name
)
VALUES
    (1, 1, 'main_stop'),
    (2, 2, 'stop2'),
    (3, 3, 'stop3'),
    (4, 4, 'stop4');

INSERT INTO config.routes (
    route_id,
    name
)
VALUES (
           1,
           'route1'
       );

INSERT INTO config.route_points (
    route_id,
    point_id,
    point_order
)
VALUES
    (1, 1, 1),
    (1, 2, 2),
    (1, 3, 3),
    (1, 4, 4);

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
             '2020-05-28T10:40:55+0000'
         );

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
             '[2020-06-04 10:30, 2020-06-04 14:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             10
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
             'route1',
             '[2020-06-03 10:30, 2020-06-03 14:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             10
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
             'route1',
             '[2020-06-05 10:30, 2020-06-05 14:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             10
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
             'route1',
             '[2020-06-04 16:30, 2020-06-04 17:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             10
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             'aaaaaaaa-aaaa-aaaa-aaaa-000000000001',
             'route1',
             '[2020-06-04 16:30, 2020-06-04 17:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             0
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             'aaaaaaaa-aaaa-aaaa-aaaa-000000000002',
             'route1',
             '[2020-06-04 16:30, 2020-06-04 17:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             1
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             'aaaaaaaa-aaaa-aaaa-aaaa-000000000003',
             'route1',
             '[2020-11-21 12:00, 2020-11-21 13:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             1
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             'aaaaaaaa-aaaa-aaaa-aaaa-000000000004',
             'route1',
             '[2020-11-21 13:00, 2020-11-21 14:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             1
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             'aaaaaaaa-aaaa-aaaa-aaaa-000000000005',
             'route1',
             '[2020-11-21 13:30, 2020-11-21 13:40]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             1
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             'aaaaaaaa-aaaa-aaaa-aaaa-000000000006',
             'route1',
             '[2020-11-21 13:30, 2020-11-21 18:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             1
         );

INSERT INTO state.drivers_workshifts_subscriptions (
    workshift_id,
    driver_id,
    status,
    subscribed_at
) VALUES (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             ('dbid0', 'uuid0')::db.driver_id,
             'ongoing',
             '2020-09-14T10:15:16+0000'
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
             ('dbid0', 'uuid0')::db.driver_id,
             'finished',
             '2020-09-14T10:15:16+0000'
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
             ('dbid0', 'uuid0')::db.driver_id,
             'planned',
             '2020-09-14T10:15:16+0000'
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
             ('dbid0', 'uuid0')::db.driver_id,
             'planned',
             '2020-09-14T10:15:16+0000'
         );

WITH shuttle_ins AS (
INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    started_at,
    capacity,
    ticket_length,
    subscription_id
)
VALUES (
    1,
    ('dbid0', 'uuid0')::db.driver_id,
    1,
    '2020-06-03T10:15:16+0000',
    16,
    3,
    1
    )
    RETURNING
    shuttle_id
    )
INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    begin_stop_id,
    lap,
    next_stop_id,
    updated_at,
    advanced_at
)
SELECT
    shuttle_ins.shuttle_id,
    1,
    1,
    2,
    NOW(),
    NOW()
FROM
    shuttle_ins
;
