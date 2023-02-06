INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.642933,55.735054)),
    (3, point(37.643129,55.734452)),
    (4, point(37.643148,55.734349)),
    (5, point(37.643055,55.734163)),
    (6, point(37.642023,55.734035)),
    (7, point(37.639663,55.737276)),
    (8, point(37.641867,55.737651));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 3, 'stop2', 'stop__2'),
    (3, 5, 'stop3', 'stop__3'),
    (4, 6, 'stop4', NULL),
    (5, 7, 'stop5', NULL),
    (6, 8, 'stop6', NULL);

INSERT INTO config.routes (
    route_id, name, is_cyclic
)
VALUES
    (1, 'route1', TRUE),
    (2, 'route2', TRUE),
    (3, 'route3', FALSE);

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
    (2, 1, 6),
    (2, 2, 5),
    (2, 3, 4),
    (2, 4, 3),
    (2, 5, 2),
    (2, 6, 1),
    (3, 1, 1),
    (3, 2, 2),
    (3, 3, 3);


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
 ),
 (
     '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
     'route2',
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
     '(30,50)'::db.driver_personal_goal
);

INSERT INTO config.workshifts (
    template_id,
    workshift_id,
    route_name,
    work_time,
    created_at,
    max_simultaneous_subscriptions
)
VALUES ( '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
         '427a330d-2506-464a-accf-346b31e288b8',
         'route1',
         '[2020-01-17T14:00:00+0000, 2020-01-17T18:00:00+0000]'::tsrange,
         NOW() AT TIME ZONE 'UTC',
         10),
       ('2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        '427a330d-2506-464a-accf-346b31e288b7',
        'route1',
        '[2020-01-17T10:00:00+0000, 2020-01-17T14:00:00+000]'::tsrange,
        NOW() AT TIME ZONE 'UTC',
        10),
       ('2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        '427a330d-2506-464a-accf-346b31e288b6',
        'route1',
        '[2020-01-16T14:00:00+0000, 2020-01-16T16:00:00+0000]'::tsrange,
        NOW() AT TIME ZONE 'UTC',
        10),
       ('2fef68c9-25d0-4174-9dd0-bdd1b3730777',
        '427a330d-2506-464a-accf-346b31e288c1',
        'route2',
        '[2020-01-12T14:00:00+0000, 2020-01-12T16:00:00+0000]'::tsrange,
        NOW() AT TIME ZONE 'UTC',
        2),
       ('2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        '427a330d-2506-464a-accf-346b31e288c2',
        'route1',
        '[2020-01-16T14:00:00+0000, 2020-01-16T16:00:00+0000]'::tsrange,
        NOW() AT TIME ZONE 'UTC',
        2);

INSERT INTO state.drivers_workshifts_subscriptions (
    subscription_id,
    workshift_id,
    driver_id,
    status,
    subscribed_at
) VALUES (1,
          '427a330d-2506-464a-accf-346b31e288b8',
          ('111', '888')::db.driver_id,
          'planned',
          '2020-09-14T10:15:16+0000'
         ),
         (2,
          '427a330d-2506-464a-accf-346b31e288c1',
          ('111', '888')::db.driver_id,
          'planned',
          '2020-09-14T10:15:16+0000'
         ),
         (3,
          '427a330d-2506-464a-accf-346b31e288c2',
          ('111', '889')::db.driver_id,
          'planned',
          '2020-09-14T10:15:16+0000'
         ),
         (4,
          '427a330d-2506-464a-accf-346b31e288c1',
          ('111', '889')::db.driver_id,
          'planned',
          '2020-09-14T10:15:16+0000'
         )
;
