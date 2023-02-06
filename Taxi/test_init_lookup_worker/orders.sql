INSERT INTO fleet.guaranteed_order (
  id,
  park_id,
  contractor_id,
  created_at,
  location_from,
  locations_to,
  client_booked_at,
  processed_at,
  record_created_at,
  record_updated_at
)
VALUES (
  'order_id1',
  'park_id1',
  'driver_id1',
  '2021-09-02T15:59:00Z',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-02T20:00:00Z',
  NULL,
  '2021-09-02T16:00:00Z',
  '2021-09-02T16:00:00Z'
),(
  'order_id2',
  'park_id2',
  'driver_id2',
  '2021-09-02T16:59:00Z',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-02T22:10:00Z',
  '2021-09-02T21:10:00Z',
  '2021-09-02T17:00:00Z',
  '2021-09-02T17:00:00Z'
),(
  'order_id3',
  'park_id3',  
  'driver_id3',
  '2021-09-02T17:09:00Z',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-02T22:05:00Z',
  NULL,
  '2021-09-02T17:10:00Z',
  '2021-09-02T17:10:00Z'
),(
  'order_id4',
  'park_id4',
  'driver_id4',
  '2021-09-02T17:10:00Z',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-02T22:21:00Z',
  NULL,
  '2021-09-02T17:11:00Z',
  '2021-09-02T17:11:00Z'
),(
  'order_id5',
  NULL,
  NULL,
  '2021-09-02T17:10:00Z',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-02T22:21:00Z',
  NULL,
  '2021-09-02T17:11:00Z',
  '2021-09-02T17:11:00Z'
);
