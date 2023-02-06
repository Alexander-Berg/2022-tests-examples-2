INSERT INTO config.points
    (point_id, position)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.642933,55.735054)),
    (3, point(37.643129,55.734452)),
    (4, point(37.643037,55.734242)),
    (5, point(37.642790,55.734062)),
    (6, point(37.642023,55.734035)),
    (7, point(37.639896,55.737345)),
    (8, point(37.641867,55.737651));

INSERT INTO config.stops
    (stop_id, point_id, name, ya_transport_stop_id)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 3, 'stop2', 'stop__2'),
    (3, 5, 'stop3', 'stop__3'),
    (4, 6, 'stop4', NULL),
    (5, 7, 'stop5', NULL),
    (6, 8, 'stop6', NULL);

INSERT INTO config.routes
    (route_id, name, is_cyclic)
VALUES
    (1, 'route1', TRUE);

INSERT INTO config.route_points
    (route_id, point_id, point_order)
VALUES
    (1, 1, 1),
    (1, 2, 2),
    (1, 3, 3),
    (1, 4, 4),
    (1, 5, 5),
    (1, 6, 6),
    (1, 7, 7),
    (1, 8, 8);

INSERT INTO config.workshift_templates
    (
        template_id,
        route_name,
        schedule,
        max_simultaneous_subscriptions,
        in_operation_since,
        deprecated_since,
        personal_goal,
        pause_duration,
        max_pauses_allowed,
        simultaneous_pauses_per_shift
    )
VALUES
    (
        '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        'route1',
        '{
          "timezone":"UTC",
          "intervals": [
            {
              "exclude": false,
              "day": [4]
            },
            {
              "exclude": false,
              "daytime": [
                {
                  "from": "10:30:00",
                  "to": "14:00:00"
                }
              ]
            }
          ]
        }'::JSONB,
        10,
        '2020-05-28T10:40:55+0000',
        '2021-05-28T10:40:55+0000',
        NULL,
        '00:10:00'::interval,
        1,
        1
    );

INSERT INTO config.workshifts
    (
        workshift_id,
        template_id,
        route_name,
        work_time,
        created_at,
        max_simultaneous_subscriptions,
        pause_duration,
        max_pauses_allowed,
        simultaneous_pauses_per_shift
    )
VALUES
    (
        '427a330d-2506-464a-accf-346b31e288b8',
        '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        'main_route',
        '[2020-06-04 10:30, 2020-06-04 14:00]'::TSRANGE,
        NOW() AT TIME ZONE 'UTC',
        10,
        '00:10:00'::interval,
        1,
        1
    );
