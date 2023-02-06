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
    name
)
VALUES
    (1, 1, 'main_stop'),
    (2, 2, 'stop2'),
    (3, 3, 'stop3'),
    (4, 4, 'stop4');

INSERT INTO config.routes (
    route_id,
    name,
    is_dynamic
)
VALUES
    (1, 'main_route', False),
    (3, 'dynamic_route', True);

INSERT INTO config.route_points (
  route_id,
  point_id,
  point_order
)
VALUES
    (1, 1, 1),
    (1, 2, 2),
    (1, 3, 3),
    (1, 4, 4),
    (3, 1, 1),
    (3, 2, 2),
    (3, 4, 4);

INSERT INTO state.route_views (
    view_id, route_id, current_view, traversal_plan
)
VALUES
    (1, 1, ARRAY[2, 3, 4],
     ROW(ARRAY[
         (2, NULL, NULL)::db.traversal_plan_point,
         (3, NULL, NULL)::db.traversal_plan_point,
         (4, NULL, NULL)::db.traversal_plan_point])::db.traversal_plan),
    (2, 3, ARRAY[2, 4],
     ROW(ARRAY[
         (2, NULL, NULL)::db.traversal_plan_point,
         (4, NULL, NULL)::db.traversal_plan_point])::db.traversal_plan);

INSERT INTO config.workshift_templates (
    template_id,
    route_name,
    schedule,
    max_simultaneous_subscriptions,
    in_operation_since
) VALUES (
  '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
  'dynamic_route',
  '{
    "timezone":"UTC",
    "intervals": [
    {
      "exclude": false,
      "daytime": [{
        "from": "14:15:00",
        "to": "20:00:00"
      }
      ]
    }]}'::JSONB,
  10,
  '2020-09-14T00:00:00+0000'
);

INSERT INTO config.workshifts (
    template_id,
    workshift_id,
    route_name,
    work_time,
    created_at,
    max_simultaneous_subscriptions,
    personal_goal,
    max_pauses_allowed,
    pause_duration,
    simultaneous_pauses_per_shift

) VALUES (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    'dynamic_route',
    '[2020-09-14 14:15, 2020-09-14 20:00]'::TSRANGE,
    NOW() AT TIME ZONE 'UTC',
    10,
    NULL,
    1,
    '12 seconds'::interval,
    1
), (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    'dynamic_route',
    '[2020-09-14 14:15, 2020-09-14 20:00]'::TSRANGE,
    NOW() AT TIME ZONE 'UTC',
    10,
    NULL,
    1,
    '10 minutes'::interval,
    1
), (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
    'dynamic_route',
    '[2020-09-14 14:15, 2020-09-14 20:00]'::TSRANGE,
    NOW() AT TIME ZONE 'UTC',
    10,
    NULL,
    2,
    '10 minutes'::interval,
    2
), (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
    'dynamic_route',
    '[2020-09-14 14:15, 2020-09-14 20:00]'::TSRANGE,
    NOW() AT TIME ZONE 'UTC',
    10,
    NULL,
    0,
    '0 seconds'::interval,
    0
), (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
    'dynamic_route',
    '[2020-09-14 14:15, 2020-09-14 20:00]'::TSRANGE,
    NOW() AT TIME ZONE 'UTC',
    10,
    NULL,
    1,
    '900 seconds'::interval,
    1
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
    ('dbid_0', 'uuid_0')::db.driver_id,
    'ongoing',
    '2020-09-14T10:15:16+0000'
), (
    2,
    '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
    ('dbid_1', 'uuid_1')::db.driver_id,
    'ongoing',
    '2020-09-14T10:15:16+0000'
), (
    3,
    '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
    ('dbid_2', 'uuid_2')::db.driver_id,
    'ongoing',
    '2020-09-14T10:15:16+0000'
), (
    4,
    '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
    ('dbid_3', 'uuid_3')::db.driver_id,
    'ongoing',
    '2020-09-14T10:15:16+0000'
), (
    5,
    '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
    ('dbid_4', 'uuid_4')::db.driver_id,
    'ongoing',
    '2020-09-14T10:15:16+0000'
), (
    6,
    '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
    ('dbid_5', 'uuid_5')::db.driver_id,
    'ongoing',
    '2020-09-14T10:15:16+0000'
);

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    capacity,
    ticket_length,
    work_mode,
    view_id,
    subscription_id,
    remaining_pauses
)
VALUES
    (1, ('dbid_0', 'uuid_0')::db.driver_id, 1, 16, 3, 'shuttle_fix', 1, 1, 0),
    (2, ('dbid_1', 'uuid_1')::db.driver_id, 3, 16, 3, 'shuttle_fix', 2, 2, 1),
    (3, ('dbid_2', 'uuid_2')::db.driver_id, 3, 16, 3, 'shuttle_fix', 2, 3, 0),
    (4, ('dbid_3', 'uuid_3')::db.driver_id, 3, 16, 3, 'shuttle_fix', 2, 4, 0),
    (5, ('dbid_4', 'uuid_4')::db.driver_id, 3, 16, 3, 'shuttle_fix', 2, 5, 1),
    (6, ('dbid_5', 'uuid_5')::db.driver_id, 3, 16, 3, 'shuttle_fix', 2, 6, 0);

INSERT INTO state.shuttle_trip_progress (
  shuttle_id,
  begin_stop_id,
  lap,
  next_stop_id,
  updated_at,
  advanced_at
)
VALUES
  (1, 1, 1, 2, NOW(), NOW()),
  (2, 1, 1, 2, NOW(), NOW()),
  (3, 1, 1, 2, NOW(), NOW()),
  (4, 1, 1, 2, NOW(), NOW()),
  (5, 1, 1, 2, NOW(), NOW());

INSERT INTO state.pauses (
    pause_id,
    shuttle_id,
    pause_requested,
    expected_pause_start,
    pause_started,
    expected_pause_finish,
    pause_finished
) VALUES (
    1,
    1,
    '2020-05-28T11:40:55+0000',
    NULL,
    '2020-05-28T11:41:55+0000',
    NULL,
    '2020-05-28T11:45:55+0000'
), (
    2,
    1,
    '2020-05-28T12:40:55+0000',
    NULL,
    NULL,
    NULL,
    NULL
), (
    3,
    3,
    '2020-05-28T12:40:55+0000',
    NULL,
    '2020-05-28T12:41:55+0000',
    '2020-05-28T12:51:55+0000',
    NULL
), (
    4,
    5,
    '2020-05-28T12:40:55+0000',
    NULL,
    NULL,
    NULL,
    NULL
);

UPDATE state.shuttles
SET pause_state = 'requested',
    pause_id = 2
WHERE shuttle_id = 1;

UPDATE state.shuttles
SET pause_state = 'in_work',
    pause_id = 3
WHERE shuttle_id = 3;

UPDATE state.shuttles
SET pause_state = 'requested',
    pause_id = 4
WHERE shuttle_id = 6;

ALTER SEQUENCE state.pauses_pause_id_seq RESTART WITH 5;

INSERT INTO state.matching_offers(
    offer_id,
    shuttle_id,
    order_point_a,
    order_point_b,
    pickup_stop_id,
    pickup_lap,
    dropoff_stop_id,
    dropoff_lap,
    price,
    expires_at,
    created_at,
    route_id
)
VALUES
    ('acfff773-398f-4913-b9e9-03bf5eda22ac', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1);

INSERT INTO state.passengers (
    booking_id,
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    shuttle_lap,
    status,
    offer_id,
    dropoff_lap
) VALUES (
             'acfff773-398f-4913-b9e9-03bf5eda22ac',
             '012345678',
             'userid_1',
             2,
             2,
             4,
             1,
             'driving',
             'acfff773-398f-4913-b9e9-03bf5eda22ac',
             1
         );

INSERT INTO state.booking_tickets (
    booking_id,
    code,
    status
) VALUES (
             'acfff773-398f-4913-b9e9-03bf5eda22ac',
             'code1',
             'issued'
         );
