INSERT INTO config.points (
    point_id, position
)
VALUES
    (1, point(37.50, 55.75)),
    (2, point(37.51, 55.75)),
    (3, point(37.52, 55.75)), -- not in route view
    (4, point(37.53, 55.75))
;

INSERT INTO config.stops (
    stop_id, point_id, name, ya_transport_stop_id
)
VALUES
    (1, 1, 'stop1', NULL),
    (2, 2, 'stop2', 'stop__2'),
    (3, 3, 'stop3', 'stop__3'),
    (4, 4, 'stop4', NULL)
;

INSERT INTO config.routes (
    route_id, name, is_dynamic
)
VALUES
    (1, 'route1', TRUE)
;

INSERT INTO config.route_points (
  route_id, point_id, point_order
)
VALUES
  (1, 1, 1),
  (1, 2, NULL),
  (1, 3, NULL),
  (1, 4, 3)
;

INSERT INTO state.route_views (
  route_id, current_view, traversal_plan
)
VALUES
  (1, ARRAY[2, 4],
   ROW(ARRAY[
       (2, '427a330d-2506-464a-accf-346b31e288b9', TRUE)::db.traversal_plan_point,
       (2, '2fef68c9-25d0-4174-9dd0-bdd1b3730775', FALSE)::db.traversal_plan_point,
       (4, '427a330d-2506-464a-accf-346b31e288b9', FALSE)::db.traversal_plan_point])::db.traversal_plan)
;

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
    '[2020-09-13 10:30, 2020-09-13 14:00]'::TSRANGE,
    NOW() AT TIME ZONE 'UTC',
    10
);

INSERT INTO state.drivers_workshifts_subscriptions (
    subscription_id,
    workshift_id,
    driver_id,
    status,
    subscribed_at,
    is_active
) VALUES (
    1,
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    ('dbid0', 'uuid0')::db.driver_id,
    'ongoing',
    '2019-09-14T10:15:16+0000',
    TRUE
);

INSERT INTO state.shuttles (
    driver_id, route_id, capacity, ticket_length, work_mode, view_id, ticket_check_enabled, subscription_id
)
VALUES
    (('dbid0', 'uuid0')::db.driver_id, 1, 16, 3, 'shuttle_fix', 1, TRUE, 1)
;

INSERT INTO state.shuttle_trip_progress (
  shuttle_id,
  lap,
  begin_stop_id,
  next_stop_id,
  updated_at,
  advanced_at,
  block_reason,
  processed_at
)
VALUES
  (1, 1, 1, 2, '2020-09-14T10:15:16+0000', '2020-09-14T10:15:16+0000', 'none', '2020-09-14T10:15:16+0000')
;

ALTER TABLE state.passengers
    DISABLE TRIGGER passenger_ticket_for_booking_trigger;

INSERT INTO state.matching_offers (
    offer_id,
    yandex_uid,
    shuttle_id,
    route_id,
    order_point_a,
    order_point_b,
    pickup_stop_id,
    pickup_lap,
    dropoff_stop_id,
    dropoff_lap,
    price,
    passengers_count,
    created_at,
    expires_at
)
VALUES
('2fef68c9-25d0-4174-9dd0-bdd1b3730775', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000'),
('427a330d-2506-464a-accf-346b31e288b9', '0123456789', 1, 1, point(30, 60), point(31, 61), 1, 1, 2, 1, '(10,RUB)', 1, '2020-01-17T18:00:00+0000', '2020-01-17T18:18:00+0000');

INSERT INTO state.passengers (
    yandex_uid,
    user_id,
    shuttle_id,
    stop_id,
    dropoff_stop_id,
    booking_id,
    offer_id,
    status,
    ticket,
    dropoff_lap
)
VALUES (
           '0123456789',
           'userid_1',
           1,
           1,
           2,
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
           'transporting',
           '123',
            1
       ), (
           '9012345678',
           'userid_2',
           1,
           2,
           4,
           '427a330d-2506-464a-accf-346b31e288b9',
           '427a330d-2506-464a-accf-346b31e288b9',
           'driving',
           '124',
           1
)
;

ALTER TABLE state.passengers
    ENABLE TRIGGER passenger_ticket_for_booking_trigger;

INSERT INTO state.booking_tickets (
    booking_id,
    status,
    code
) VALUES (
    '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
    'confirmed',
    '123'
), (
    '427a330d-2506-464a-accf-346b31e288b9',
    'issued',
    '124'
)
;
