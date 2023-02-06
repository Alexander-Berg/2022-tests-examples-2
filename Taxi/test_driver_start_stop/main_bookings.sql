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
('acfff773-398f-4913-b9e9-03bf5eda22ac', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1),
('acfff773-398f-4913-b9e9-03bf5eda22ad', 1, point(30, 60), point(30, 60), 1, 1, 1, 2, (40.5, 'RUB')::db.trip_price, '2022-01-20T16:00:00+0000', '2020-01-20T16:48:00+0000', 1);

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
  dropoff_lap,
  created_at
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
  4,
  '2022-01-20T16:00:00+0000'
), (
  'acfff773-398f-4913-b9e9-03bf5eda22ad',
  '012345679',
  'userid_2',
  2,
  1,
  2,
  1,
  'transporting',
  'acfff773-398f-4913-b9e9-03bf5eda22ad',
  2,
  '2022-01-20T16:00:00+0000'
);

INSERT INTO state.booking_tickets (
  booking_id,
  code,
  status
) VALUES (
  'acfff773-398f-4913-b9e9-03bf5eda22ac',
  'code1',
  'issued'
), (
  'acfff773-398f-4913-b9e9-03bf5eda22ad',
  'code2',
  'confirmed'
);
