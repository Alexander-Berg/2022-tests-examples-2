INSERT INTO config.points (
    point_id,
    position
)
VALUES
    (1, point(37.642853,55.735233)),
    (2, point(37.642933,55.735054)),
    (3, point(37.643129,55.734452)),
    (4, point(37.643148,55.734349)),
    (5, point(37.643122,55.734351));

INSERT INTO config.stops (
    stop_id,
    point_id,
    name
)
VALUES
    (1, 1, 'main_stop'),
    (2, 2, 'stop2'),
    (3, 3, 'stop3'),
    (4, 4, 'stop4'),
    (5, 5, 'stop5');

INSERT INTO config.routes (
    route_id,
    name,
    is_dynamic
)
VALUES (
    1,
    'main_route',
    TRUE
);

INSERT INTO config.route_points (
  route_id,
  point_id,
  point_order
)
VALUES
    (1, 1, 1),
    (1, 2, NULL),
    (1, 3, NULL),
    (1, 4, 2),
    (1, 5, 3);

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
    ('dbid_0', 'uuid_1')::db.driver_id,
    'ongoing',
    '2020-09-14T10:15:16+0000'
);

INSERT INTO state.route_views (
    route_id, current_view, traversal_plan
)
VALUES
    (1, ARRAY[1, 2, 4],
     ROW(ARRAY[
         (1, '3a46a5df-90d1-413f-85ab-8efb562676fb', TRUE)::db.traversal_plan_point,
         (1, '43bdb9b8-ee06-4eac-b430-665788b29d53', TRUE)::db.traversal_plan_point,
         (2, '3a46a5df-90d1-413f-85ab-8efb562675fb', TRUE)::db.traversal_plan_point,
         (2, '43bdb9b8-ee06-4eac-b430-665788b29d53', FALSE)::db.traversal_plan_point,
         (4, '3a46a5df-90d1-413f-85ab-8efb562675fb', FALSE)::db.traversal_plan_point,
         (4, '3a46a5df-90d1-413f-85ab-8efb562676fb', FALSE)::db.traversal_plan_point])::db.traversal_plan)
;

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    capacity,
    ticket_length,
    work_mode,
    subscription_id,
    view_id
)
VALUES (
    1,
    ('dbid_0', 'uuid_1')::db.driver_id,
    1,
    16,
    3,
    'shuttle_fix',
    1,
    1
);

INSERT INTO state.shuttle_trip_progress (
    shuttle_id,
    lap,
    begin_stop_id,
    next_stop_id,
    updated_at,
    advanced_at
)
VALUES
    (1, 0, 1, 1, NOW(), NOW())
;

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
    ('43bdb9b8-ee06-4eac-b430-665788b29d53', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1),
    ('3a46a5df-90d1-413f-85ab-8efb562675fb', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1),
    ('3a46a5df-90d1-413f-85ab-8efb562676fb', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1);

INSERT INTO state.passengers (
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    booking_id,
    offer_id,
    status,
    dropoff_lap
)
VALUES
    (
        'yandex_uid_1',
        'userid_1',
        1,
        1,
        2,
        '43bdb9b8-ee06-4eac-b430-665788b29d53',
        '43bdb9b8-ee06-4eac-b430-665788b29d53',
        'driving',
        1
    ),
    (
        'yandex_uid_2',
        'userid_2',
        1,
        2,
        4,
        '3a46a5df-90d1-413f-85ab-8efb562675fb',
        '3a46a5df-90d1-413f-85ab-8efb562675fb',
        'driving',
        1
    ),
    (
        'yandex_uid_3',
        'userid_3',
        1,
        1,
        4,
        '3a46a5df-90d1-413f-85ab-8efb562676fb',
        '3a46a5df-90d1-413f-85ab-8efb562676fb',
        'transporting',
        1
    )
;

INSERT INTO state.booking_tickets (
    booking_id,
    status,
    code
)
VALUES
    ('3a46a5df-90d1-413f-85ab-8efb562676fb', 'confirmed', '123'),
    ('43bdb9b8-ee06-4eac-b430-665788b29d53', 'issued', '012'),
    ('3a46a5df-90d1-413f-85ab-8efb562675fb', 'issued', '234');
