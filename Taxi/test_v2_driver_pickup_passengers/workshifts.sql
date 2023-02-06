INSERT INTO config.workshift_templates (
    template_id,
    route_name,
    schedule,
    max_simultaneous_subscriptions,
    in_operation_since,
    deprecated_since,
    personal_goal
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
     '2020-05-28T10:40:55+0000',
     '2021-05-28T10:40:55+0000',
     NULL
 );

INSERT INTO config.workshifts (
    workshift_id,
    template_id,
    route_name,
    work_time,
    created_at,
    max_simultaneous_subscriptions
) VALUES (
    '427a330d-2506-464a-accf-346b31e288b8',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    'main_route',
    '[2020-06-04 10:30, 2020-06-04 14:00]'::TSRANGE,
    NOW() AT TIME ZONE 'UTC',
    10
);

INSERT INTO state.drivers_workshifts_subscriptions (
    subscription_id,
    workshift_id,
    driver_id,
    subscribed_at,
    status
) VALUES
    (
        1,
        '427a330d-2506-464a-accf-346b31e288b8',
        ('111', '888')::db.driver_id,
        '2020-06-03T10:15:16+0000',
        'planned'
    ),
    (
        2,
        '427a330d-2506-464a-accf-346b31e288b8',
        ('dbid_0', 'uuid_1')::db.driver_id,
        '2020-06-03T10:15:16+0000',
        'planned'
    ),
    (
        3,
        '427a330d-2506-464a-accf-346b31e288b8',
        ('dbid_0', 'uuid_0')::db.driver_id,
        '2020-06-03T10:15:16+0000',
        'planned'
    ),
    (
        4,
        '427a330d-2506-464a-accf-346b31e288b8',
        ('dbid_1', 'uuid_1')::db.driver_id,
        '2020-06-03T10:15:16+0000',
        'planned'
    );

UPDATE state.shuttles
SET subscription_id = 2
WHERE shuttle_id = 1;

UPDATE state.shuttles
SET subscription_id = 4
WHERE shuttle_id = 2;
