INSERT INTO fleet.guaranteed_order (
  id,
  park_id,
  contractor_id,
  created_at,
  location_from,
  locations_to,
  client_booked_at,
  processed_at,
  cancelled_at,
  record_created_at,
  record_updated_at,
  zone_id,
  tariff_class
)
VALUES (
  'order_id1',
  NULL,
  NULL,
  '2021-09-02T15:59:00Z',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-03T04:00:00Z',
  NULL,
  NULL,
  '2021-09-02T16:00:00Z',
  '2021-09-02T16:00:00Z',
  'moscow',
  'econom'
),(
  'order_id2',
  'park_id2',
  'driver_id2',
  '2021-09-02T16:59:00Z',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-03T04:00:00Z',
  '2021-09-02T21:10:00Z',
  NULL,
  '2021-09-02T17:00:00Z',
  '2021-09-02T17:00:00Z',
  'moscow',
  'econom'
),(
  'order_id3',
  NULL,  
  NULL,
  '2021-09-02T17:09:00Z',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-03T04:00:00Z',
  NULL,
  '2021-09-02T21:10:00Z',
  '2021-09-02T17:10:00Z',
  '2021-09-02T17:10:00Z',
  'moscow',
  'econom'
),(
  'order_id4',
  NULL,
  NULL,
  '2021-09-02T17:10:00Z',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-03T04:00:00Z',
  NULL,
  NULL,
  '2021-09-02T17:11:00Z',
  '2021-09-02T17:11:00Z',
  'moscow',
  'econom'
),(
  'order_id5',
  NULL,
  NULL,
  '2021-09-02T17:10:00Z',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-03T04:00:00Z',
  NULL,
  NULL,
  '2021-09-02T17:11:00Z',
  '2021-09-02T17:11:00Z',
  'berlin',
  'comfort'
);

INSERT INTO fleet.order_candidates (
  order_id, 
  candidates, 
  updated_at
) 
VALUES (
  'order_id1', 
  ARRAY['1', '2', '3'], 
  '2021-09-02 20:00:00.000000 +00:00'
),(
  'order_id2', 
  ARRAY['1', '2', '3'], 
  '2021-09-02 20:00:00.000000 +00:00'
),(
  'order_id3', 
  ARRAY['1', '2', '3'], 
  '2021-09-02 20:00:00.000000 +00:00'
),(
  'order_id4', 
  ARRAY['1', '2', '3'], 
  '2021-09-02 21:50:00.000000 +00:00'
),(
  'order_id5', 
  ARRAY['1', '2', '3'], 
  '2021-09-02 20:00:00.000000 +00:00'
);
