INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.642933,55.735054)),
    (3, point(37.643129,55.734452)),
    (4, point(37.643148,55.734349)),
    (5, point(37.643055,55.734163)),
    (6, point(37.642023,55.734035));

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 3, 'stop2', 'stop__2'),
    (3, 5, 'stop3', 'stop__3'),
    (4, 6, 'stop4', NULL);

INSERT INTO config.routes (
    route_id, name, is_cyclic
)
VALUES
    (1, 'route1', TRUE);

INSERT INTO config.route_points (
    route_id, point_id, point_order
)
VALUES
    (1, 1, 1),
    (1, 2, 2),
    (1, 3, 3),
    (1, 4, 4),
    (1, 5, 5),
    (1, 6, 6);

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
    max_simultaneous_subscriptions,
    personal_goal
) VALUES (
     '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
     '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
     'route1',
     '[2020-06-04 10:30, 2020-06-04 14:00]'::TSRANGE,
     NOW() AT TIME ZONE 'UTC',
     10,
     NULL
), (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    'route1',
    '[2020-06-04 10:30, 2020-06-04 14:00]'::TSRANGE,
    NOW() AT TIME ZONE 'UTC',
    10,
    '(30,50)'::db.driver_personal_goal
);

INSERT INTO state.drivers_workshifts_subscriptions (
    subscription_id,
    workshift_id,
    driver_id,
    status,
    subscribed_at
) VALUES (
    1,
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    ('dbid0', 'uuid0')::db.driver_id,
    'planned',
    '2020-09-14T10:15:16+0000'
), (
    2,
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    ('dbid0', 'uuid0')::db.driver_id,
    'planned',
    '2020-09-14T10:15:16+0000'
), (
    3,
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    ('dbid1', 'uuid1')::db.driver_id,
    'ongoing',
    '2020-09-14T10:15:16+0000'
), (
    4,
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    ('dbid2', 'uuid2')::db.driver_id,
    'missed',
    '2020-09-14T10:15:16+0000'
), (
    5,
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    ('dbid3', 'uuid3')::db.driver_id,
    'finished',
    '2020-09-14T10:15:16+0000'
);
