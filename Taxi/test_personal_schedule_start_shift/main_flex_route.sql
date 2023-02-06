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
    name,
    is_terminal
)
VALUES
    (1, 1, 'main_stop', TRUE),
    (2, 2, 'stop2', FALSE),
    (3, 3, 'stop3', FALSE),
    (4, 4, 'stop4', TRUE);

INSERT INTO config.routes (
    route_id,
    name,
    is_dynamic
)
VALUES (
    1,
    'route1',
    TRUE
);

INSERT INTO config.route_points (
  route_id,
  point_id,
  point_order
)
VALUES
    (1, 1, NULL),
    (1, 2, NULL),
    (1, 3, NULL),
    (1, 4, NULL);

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
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    ('dbid1', 'uuid1')::db.driver_id,
    'missed',
    '2020-09-14T10:15:16+0000'
), (
    3,
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    ('dbid2', 'uuid2')::db.driver_id,
    'finished',
    '2020-09-14T10:15:16+0000'
);
