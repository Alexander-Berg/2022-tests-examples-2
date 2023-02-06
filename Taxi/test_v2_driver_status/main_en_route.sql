INSERT INTO config.points (
    point_id,
    position
)
VALUES
(
    1,
    point(30, 60)
),
(
    2,
    point(30, 61)
),
(
    3,
    point(30, 62)
),
(
    4,
    point(30, 63)
)
;

INSERT INTO config.stops (
    stop_id,
    point_id,
    name
)
VALUES
(
    1,
    2,
    'first_stop'
),
(
    2,
    3,
    'second_stop'
),
(
    3,
    4,
    'last_stop'
)
;

INSERT INTO config.routes (
    route_id,
    name
)
VALUES (
    1,
    'main_route'
);

INSERT INTO config.route_points (
  route_id,
  point_id,
  point_order
)
VALUES
(
  1,
  1,
  1
),
(
  1,
  2,
  2
),
(
  1,
  3,
  3
),
(
  1,
  4,
  4
)
;

INSERT INTO state.shuttles (
    shuttle_id,
    driver_id,
    route_id,
    capacity,
    ticket_length,
    work_mode
)
VALUES (
    1,
    ('dbid_0', 'uuid_1')::db.driver_id,
    1,
    16,
    3,
    'shuttle_fix'
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
  'created',
  1
),
(
  'yandex_uid_2',
  'userid_2',
  1,
  2,
  3,
  '3a46a5df-90d1-413f-85ab-8efb562675fb',
  '3a46a5df-90d1-413f-85ab-8efb562675fb',
  'created',
   1
),
(
  'yandex_uid_3',
  'userid_3',
  1,
  1,
  2,
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
