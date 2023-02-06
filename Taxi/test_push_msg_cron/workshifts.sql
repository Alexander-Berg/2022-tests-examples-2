INSERT INTO config.workshift_templates (
    template_id,
    route_name,
    schedule,
    max_simultaneous_subscriptions,
    in_operation_since
) VALUES (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730771',
             'route1',
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
         ),
         (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730772',
             'route4',
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
             '2fef68c9-25d0-4174-9dd0-bdd1b3730771',
             '2fef68c9-25d0-4174-9dd0-bdd1b3730771',
             'route1',
             '[2019-09-14 10:00, 2019-09-14 14:00]'::TSRANGE,
             '2019-09-14T09:00:00+0000',
             10
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730772',
             '2fef68c9-25d0-4174-9dd0-bdd1b3730772',
             'route4',
             '[2019-09-14 10:00, 2019-09-14 14:00]'::TSRANGE,
             '2019-09-14T09:00:00+0000',
             10
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730771',
             '427a330d-2506-464a-accf-346b31e288b1',
             'route1',
             '[2019-09-14 10:00, 2019-09-14 18:00]'::TSRANGE,
             '2019-09-10T10:00:00+0000',
             10
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730771',
             '427a330d-2506-464a-accf-346b31e288b2',
             'route1',
             '[2019-09-14 10:00, 2019-09-14 18:00]'::TSRANGE,
             '2019-09-10T10:00:00+0000',
             10
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730771',
             '427a330d-2506-464a-accf-346b31e288b3',
             'route2',
             '[2019-09-14 10:00, 2019-09-14 18:00]'::TSRANGE,
             '2019-09-10T10:00:00+0000',
             10
         ), (
             '2fef68c9-25d0-4174-9dd0-bdd1b3730771',
             '427a330d-2506-464a-accf-346b31e288b4',
             'route3',
             '[2019-09-14 10:00, 2019-09-14 18:00]'::TSRANGE,
             '2019-09-10T10:00:00+0000',
             10
         )
;

INSERT INTO state.drivers_workshifts_subscriptions (
    subscription_id,
    workshift_id,
    driver_id,
    subscribed_at
) VALUES (
             1,
             '427a330d-2506-464a-accf-346b31e288b1',
             ('dbid1', 'uuid1')::db.driver_id,
             '2019-09-14T09:30:00+0000'
         ), (
             2,
             '427a330d-2506-464a-accf-346b31e288b2',
             ('some1', 'uuid5')::db.driver_id,
             '2019-09-14T09:30:00+0000'
         ), (
             3,
             '427a330d-2506-464a-accf-346b31e288b3',
             ('some2', 'uuid6')::db.driver_id,
             '2019-09-14T09:30:00+0000'
         ), (
             4,
             '427a330d-2506-464a-accf-346b31e288b4',
             ('dbid3', 'uuid3')::db.driver_id,
             '2019-09-14T09:30:00+0000'
         )
;


INSERT INTO state.drivers_workshifts_subscriptions (
    subscription_id,
    workshift_id,
    driver_id,
    status,
    subscribed_at
) VALUES (
             5,
             '2fef68c9-25d0-4174-9dd0-bdd1b3730771',
             ('dbid2', 'uuid2')::db.driver_id,
             'ongoing',
             '2019-09-14T09:30:00+0000'
         ), (
             6,
             '2fef68c9-25d0-4174-9dd0-bdd1b3730772',
             ('dbid4', 'uuid4')::db.driver_id,
             'ongoing',
             '2019-09-14T09:30:00+0000'
         )
;
