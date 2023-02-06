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
         ),
         (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
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
             '[2020-09-14 10:30, 2020-09-14 14:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             10
         ),
         (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
             'route1',
             '[2020-09-14 10:00, 2020-09-14 18:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             10
         ),
         (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
             '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
             'route1',
             '[2019-09-14 10:00, 2020-09-14 18:00]'::TSRANGE,
             NOW() AT TIME ZONE 'UTC',
             10
         );

INSERT INTO state.drivers_workshifts_subscriptions (
    subscription_id,
    workshift_id,
    driver_id,
    status,
    subscribed_at,
    is_active
) VALUES (
             11,
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             ('dbid_2', 'uuid_0')::db.driver_id,
             'finished',
             '2019-09-14T10:15:16+0000',
             true
         ),
         (
             12,
             '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
             ('dbid_2', 'uuid_1')::db.driver_id,
             'missed',
             '2019-09-14T10:15:16+0000',
          false
         ),
         (
             42,
             '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
             ('dbid_2', 'uuid_1')::db.driver_id,
             'planned',
             '2019-09-14T10:15:16+0000',
          true
         );

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    ended_at,
    capacity,
    ticket_length,
    work_mode,
    subscription_id
)
VALUES
    (
        11,
        ('dbid_2', 'uuid_0')::db.driver_id,
        1,
        '2020-05-28T11:40:55+0000',
        16,
        3,
        'shuttle_fix',
        11
    );
