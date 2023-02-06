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
             'main_route',
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
    max_simultaneous_subscriptions,
    max_pauses_allowed,
    pause_duration,
    simultaneous_pauses_per_shift
)
VALUES ( '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
         '427a330d-2506-464a-accf-346b31e288a9',
         'main_route',
         '[2020-09-14T14:15:00+0000, 2020-09-14T15:00:00+0000]'::tsrange,
         '2020-09-14T10:15:16+0000',
         '2020-09-14T10:15:16+0000',
         10,
         3,
         '30 minutes'::interval,
         2);

INSERT INTO state.drivers_workshifts_subscriptions (
    subscription_id,
    workshift_id,
    driver_id,
    subscribed_at,
    status
) VALUES (
             1,
             '427a330d-2506-464a-accf-346b31e288a9',
             ('dbid0', 'uuid0')::db.driver_id,
             '2020-09-14T10:15:16+0000',
          'planned'
         ), (
             2,
             '427a330d-2506-464a-accf-346b31e288a9',
             ('dbid1', 'uuid1')::db.driver_id,
             '2020-09-14T10:15:16+0000',
             'planned'
         ),
         (
             4,
             '427a330d-2506-464a-accf-346b31e288a9',
             ('dbid_0', 'uuid_0')::db.driver_id,
             '2020-09-14T10:15:16+0000',
             'planned'
         ),
         (
             13,
             '427a330d-2506-464a-accf-346b31e288a9',
             ('111', '999')::db.driver_id,
             '2020-09-14T10:15:16+0000',
             'planned'
         );
