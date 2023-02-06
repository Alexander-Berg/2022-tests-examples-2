INSERT INTO fleet.park_order (
  park_id,
  id,
  status,
  tariff_class,
  personal_phone_id,
  address_from,
  addresses_to,
  geopoint_from,
  geopoints_to,
  created_at,
  ended_at,
  is_creator,
  event_index,
  last_contractor_park_id,
  last_contractor_id,
  record_created_at,
  record_updated_at,
  number,
  update_seq_no
)
VALUES(
  'some_park',
  'order_id2',
  'expired',
  'econom',
  'phone_id1',
  'address_A',
  ARRAY['address_B1', 'address_B2'],
  '{37.6, 50.6}',
  '{{37.6, 51.6}, {37.6, 52.6}}',
  '2021-02-09T17:00:00Z',
  '2021-02-09T19:00:00Z',
  True,
  0,
  NULL,
  NULL,
  '2021-02-09T19:00:00Z',
  '2021-02-09T19:00:00Z',
  2,
  8
), (
  'some_park',
  'order_id3',
  'created',
  'econom',
  'phone_id1',
  'address_A',
  ARRAY['address_B1', 'address_B2'],
  '{37.6, 50.6}',
  '{{37.6, 51.6}, {37.6, 52.6}}',
  '2021-02-09T17:00:00Z',
  NULL,
  True,
  0,
  'some_park',
  'driver_id',
  '2021-02-09T19:00:00Z',
  '2021-02-09T19:00:00Z',
  3,
  1
),(
  'some_park',
  'order_id4',
  'cancelled_by_user',
  'econom',
  'phone_id1',
  'address_A',
  ARRAY['address_B1', 'address_B2'],
  '{37.6, 50.6}',
  '{{37.6, 51.6}, {37.6, 52.6}}',
  '2021-02-09T17:00:00Z',
  '2021-02-09T19:00:00Z',
  True,
  0,
  'some_park',
  'driver_id',
  '2021-02-09T19:00:00Z',
  '2021-02-09T19:00:00Z',
  4,
  2
),(
  'some_park',
  'order_id5',
  'completed',
  'econom',
  'phone_id1',
  'address_A',
  ARRAY['address_B1', 'address_B2'],
  '{37.6, 50.6}',
  '{{37.6, 51.6}, {37.6, 52.6}}',
  '2021-02-09T17:00:00Z',
  '2021-02-09T19:00:00Z',
  True,
  0,
  'some_park',
  'driver_id',
  '2021-02-09T19:00:00Z',
  '2021-02-09T19:00:00Z',
  5,
  3
),(
  'another_park',
  'order_id6',
  'cancelled_by_driver',
  'econom',
  'phone_id1',
  'address_A',
  ARRAY['address_B1', 'address_B2'],
  '{37.6, 50.6}',
  '{{37.6, 51.6}, {37.6, 52.6}}',
  '2021-02-09T17:00:00Z',
  '2021-02-09T19:00:00Z',
  True,
  0,
  'some_park',
  'driver_id',
  '2021-02-09T19:00:00Z',
  '2021-02-09T19:00:00Z',
  6,
  4
),(
  'some_park',
  'order_id7',
  'cancelled_by_driver',
  'econom',
  'phone_id1',
  'address_A',
  ARRAY['address_B1', 'address_B2'],
  '{37.6, 50.6}',
  '{{37.6, 51.6}, {37.6, 52.6}}',
  '2021-02-09T17:00:00Z',
  '2021-02-09T19:00:00Z',
  True,
  0,
  'another_park',
  'driver_id',
  '2021-02-09T19:00:00Z',
  '2021-02-09T19:00:00Z',
  7,
  5
),(
  'some_park',
  'order_id10',
  'completed',
  'econom',
  'phone_id1',
  'address_A',
  ARRAY['address_B1', 'address_B2'],
  '{37.6, 50.6}',
  '{{37.6, 51.6}, {37.6, 52.6}}',
  '2021-02-09T17:00:00Z',
  '2021-02-09T19:00:00Z',
  True,
  0,
  'another_park',
  'driver_id',
  '2021-02-09T19:00:00Z',
  '2021-02-09T19:00:00Z',
  10,
  6
), (
  'park',
  'order',
  'created',
  'econom',
  'phone_id1',
  'address_A',
  ARRAY['address_B1', 'address_B2'],
  '{37.6, 50.6}',
  '{{37.6, 51.6}, {37.6, 52.6}}',
  '2021-02-09T17:00:00Z',
  NULL,
  True,
  0,
  'park',
  'driver',
  '2021-02-09T19:00:00Z',
  '2021-02-09T19:00:00Z',
  1,
  7
);