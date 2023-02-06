INSERT INTO config.workshift_templates (
    template_id,
    route_name,
    schedule,
    pause_duration,
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
             '10 minutes'::interval,
             10,
             '2020-05-28T10:40:55+0000'
         );

INSERT INTO config.workshifts (
    template_id,
    workshift_id,
    route_name,
    work_time,
    created_at,
    pause_duration,
    max_simultaneous_subscriptions
) VALUES (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             'route1',
             '[2020-09-14 10:30, 2020-09-14 14:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             '10 minutes'::interval,
             10
         ),
         (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
             'route1',
             '[2020-09-14 10:00, 2020-09-14 18:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             '10 minutes'::interval,
             10
         );

INSERT INTO state.drivers_workshifts_subscriptions (
    subscription_id,
    workshift_id,
    driver_id,
    status,
    subscribed_at
) VALUES
    (
        9,
        '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        ('dbid1', 'uuid1')::db.driver_id,
        'ongoing',
        '2019-09-14T10:15:16+0000'
    ),
    (
        10,
        '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        ('dbid2', 'uuid2')::db.driver_id,
        'ongoing',
        '2019-09-14T10:15:16+0000'
    ),
    (
        11,
        '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        ('dbid3', 'uuid3')::db.driver_id,
        'ongoing',
        '2019-09-14T10:15:16+0000'
    ),
    (
        12,
        '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
        ('dbid4', 'uuid4')::db.driver_id,
        'ongoing',
        '2019-09-14T10:15:16+0000'
    );

INSERT INTO state.shuttles (
    shuttle_id, driver_id, route_id, capacity, ticket_length, work_mode
)
VALUES
    (4, ('dbid3', 'uuid3')::db.driver_id, 1, 16, 3, 'shuttle_fix'),
    (5, ('dbid4', 'uuid4')::db.driver_id, 1, 16, 3, 'shuttle_fix')
;



INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    lap,
    begin_stop_id,
    next_stop_id,
    updated_at,
    advanced_at,
    block_reason,
    processed_at
)
VALUES
    (4, 1, 1, 2, '2020-09-14T10:15:16+0000', '2020-09-14T10:15:16+0000', 'none', '2020-09-14T10:15:16+0000'),
    (5, 1, 1, 2, '2020-09-14T10:15:16+0000', '2020-09-14T10:15:16+0000', 'none', '2020-09-14T10:15:16+0000')
;
