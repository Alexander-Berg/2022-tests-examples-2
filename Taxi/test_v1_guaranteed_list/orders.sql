INSERT INTO fleet.guaranteed_order (
  id,
  park_id,
  contractor_id,
  location_from,
  locations_to,
  client_booked_at,
  created_at,
  cancelled_at,
  processed_at,
  record_created_at,
  record_updated_at
)
VALUES (
  'order_id1',
  'park_id1',
  'driver_id1',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-02T18:00:00Z',
  '2021-09-02T16:00:00Z',
  NULL,
  NULL,
  '2021-09-02T16:00:00Z',
  '2021-09-02T16:00:00Z'
),(
  'order_id2',
  'park_id1',
  'driver_id2',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-02T20:20:00Z',
  '2021-09-02T16:11:00Z',
  '2021-09-02T16:42:00Z',
  NULL,
  '2021-09-02T16:12:00Z',
  '2021-09-02T16:12:00Z'
),(
  'order_id3',
  'park_id1',
  'driver_id3',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-02T20:23:00Z',
  '2021-09-02T16:32:00Z',
  NULL,
  '2021-09-02T18:55:00Z',
  '2021-09-02T16:34:00Z',
  '2021-09-02T16:34:00Z'
),(
  'order_id4',
  'park_id2',
  'driver_id4',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-02T21:20:00Z',
  '2021-09-02T16:00:00Z',
  NULL,
  NULL,
  '2021-09-02T16:00:00Z',
  '2021-09-02T16:00:00Z'
),(
  'order_id5',
  NULL,
  NULL,
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-02T21:20:00Z',
  '2021-09-02T16:00:00Z',
  NULL,
  NULL,
  '2021-09-02T16:00:00Z',
  '2021-09-02T16:00:00Z'
);
