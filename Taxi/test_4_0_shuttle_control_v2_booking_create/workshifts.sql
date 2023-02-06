
INSERT INTO config.workshift_templates (
    template_id,
    route_name,
    schedule,
    max_simultaneous_subscriptions,
    in_operation_since
) VALUES (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             'main_route',
             '{
               "timezone":"UTC",
               "intervals": [{
                 "exclude": false,
                 "day": [1, 2, 3, 4, 5, 6, 7]
               }, {
                 "exclude": false,
                 "daytime": [{
                   "from": "10:00:00",
                   "to": "14:00:00"
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
             'main_route',
             '[2019-09-14 10:00, 2019-09-14 14:00]'::TSRANGE,
             '2019-09-14T09:00:00+0000',
             10
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             '427a330d-2506-464a-accf-346b31e288b8',
             'main_route',
             '[2019-09-14 10:00, 2019-09-14 10:43]'::TSRANGE,
             '2019-09-10T10:00:00+0000',
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
             '427a330d-2506-464a-accf-346b31e288b8',
             ('dbid_0', 'uuid_0')::db.driver_id,
             'planned',
             '2019-09-14T09:30:00+0000'
         ), (
             3,
             '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
             ('dbid_2', 'uuid_2')::db.driver_id,
             'ongoing',
             '2019-09-14T09:30:00+0000'
         )
;
